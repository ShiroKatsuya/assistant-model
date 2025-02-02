from typing import List, Literal, Optional
from google import genai
import tiktoken
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import get_buffer_string, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
import os
import uuid
from tavily import Client
import json
from datetime import datetime
import torch

from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from google.genai.types import (GenerateContentConfig
)

from langchain_ollama import OllamaEmbeddings

import ollama
from datetime import datetime

client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

zero_shot_prompt = """You are a helpful AI assistant with access to Google Search. When using the search tool:
1. Extract the key information from search results
2. Present the information in a clear, organized way
3. Focus on factual, up-to-date details
4. Avoid redundant information
5. Cite sources when possible"""

search = GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"]
                )


def get_realtime_data(query):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = client.models.generate_content(
            model=model_id,  
            contents=query,
            config=search
        )
        search_results = response.candidates[0].content.parts[0].text
        print("search_results : ", search_results)
        

        deepseek_response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': zero_shot_prompt
                },
                {
                    'role': 'user', 
                    'content': search_results
                }
            ]
        )
        response = deepseek_response['message']['content']
        
        # Return response in the expected state format
        return {
            "messages": [AIMessage(content=f"As of {current_time}, here's what I found:\n{response}")],
            "recall_memories": []
        }
        
    except Exception as e:
        return {
            "messages": [AIMessage(content=f"Error fetching real-time data: {str(e)}")],
            "recall_memories": []
        }


model_name = "deepseek-r1:1.5b"

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class State(MessagesState):
    recall_memories: List[str]
    conversation_history: List[dict]

def main(initial_message: str = None, second_message: str = None, full_history: List[str] = None):
    # Configure Gemini
    client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
    model_id = "gemini-2.0-flash-exp"
    # Configure Tavily
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    Client.api_key = tavily_api_key  

    def embed_text(text: str) -> List[float]:
            import google.generativeai as genai
            """Generate embeddings using Gemini model."""
            try:
                embedding = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_query"
                )
                return embedding['embedding']
            except Exception as e:
                print(f"Error generating embedding: {e}")
                return [0.0] * 768  

            
    class GeminiEmbeddings(Embeddings):
        """Wrapper class for Gemini embeddings."""
        
        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            """Generate embeddings for a list of documents."""
            return [embed_text(text) for text in texts]
            
        def embed_query(self, text: str) -> List[float]:
            """Generate embeddings for a query string."""
            return embed_text(text)

    embeddings = GeminiEmbeddings()
    recall_vector_store = InMemoryVectorStore(embeddings)

    # Modified memory loading section
    MEMORY_FILE = "ai_memories.json"
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            saved_memories = json.load(f)
            
        def filter_relevant_memories(query: str, memories: list, threshold: float = 0.9) -> list:
            """Filter memories using pre-computed embeddings and batch processing."""
            query_embedding = embeddings.embed_query(query)
            query_tensor = torch.tensor(query_embedding, device=device)
            
            # Prepare batch of memory embeddings, handle missing embeddings gracefully
            memory_embeddings = []
            valid_memories = []
            for memory in memories:
                try:
                    embedding = memory['metadata']['embedding']
                    memory_embeddings.append(embedding)
                    valid_memories.append(memory)
                except KeyError:
                    print(f"Warning: Missing embedding for memory ID {memory['id']}")
                    continue  # Skip this memory
            
            if not memory_embeddings:
                return []  # Return empty if no embeddings are available
            
            memory_embeddings_tensor = torch.tensor(memory_embeddings, device=device)
            
            # Calculate similarities in a batch
            similarities = torch.nn.functional.cosine_similarity(
                query_tensor.unsqueeze(0), 
                memory_embeddings_tensor,
                dim=1
            )
            
            relevant_memories = [
                memory for memory, similarity in zip(valid_memories, similarities) if similarity > threshold
            ]
            
            return relevant_memories

        # Only load memories relevant to the initial message if provided
        if initial_message:
            relevant_memories = filter_relevant_memories(initial_message, saved_memories)
            memory_batch = [
                Document(
                    page_content=memory['content'],
                    id=memory['id'],
                    metadata=memory['metadata']
                ) for memory in relevant_memories
            ]
            
            print(f"Loaded {len(memory_batch)} relevant memories from file.")
            
            batch_size = 64
            for i in range(0, len(memory_batch), batch_size):
                batch = memory_batch[i:i + batch_size]
                with torch.no_grad():
                    recall_vector_store.add_documents(batch)

    def get_user_id(config: RunnableConfig) -> str:
        user_id = config["configurable"].get("user_id")
        if user_id is None:
            raise ValueError("User ID needs to be provided to save a memory.")
        return user_id

    @tool
    def save_recall_memory(memory: str, config: RunnableConfig) -> str:
        """Save memory to vectorstore and persistent storage with pre-computed embeddings."""
        user_id = get_user_id(config)
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Compute embedding once and store it
        memory_embedding = embed_text(memory)
        
        document = Document(
            page_content=memory,
            id=memory_id,
            metadata={
                "user_id": user_id,
                "timestamp": timestamp,
                "type": "conversation",
                "embedding": memory_embedding  # Store the embedding
            }
        )
        
        recall_vector_store.add_documents([document])
        
        # Save to persistent storage
        memory_entry = {
            "id": memory_id,
            "content": memory,
            "metadata": {
                "user_id": user_id,
                "timestamp": timestamp,
                "type": "conversation",
                "embedding": memory_embedding  # Store the embedding
            }
        }
        
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                memories = json.load(f)
        else:
            memories = []
            
        memories.append(memory_entry)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memories, f, indent=2)
            
        return memory

    @tool
    def search_recall_memories(query: str, config: RunnableConfig) -> List[str]:
        """Search for relevant memories with improved filtering."""
        user_id = get_user_id(config)

        def _filter_function(doc: Document) -> bool:
            return doc.metadata.get("user_id") == user_id

        documents = recall_vector_store.similarity_search(
            query, 
            k=5,  # Increased number of results
            filter=_filter_function,
            search_type="similarity",
            score_threshold=0.7  # Only return relevant matches
        )
        
        # Sort by timestamp if available
        documents.sort(key=lambda x: x.metadata.get("timestamp", ""), reverse=True)
        
        return [doc.page_content for doc in documents]

    search = TavilySearchResults(max_results=1)
    tools = [save_recall_memory, search_recall_memories, search]
   # Define the prompt template for the agent
    SYSTEM_PROMPT = """You are a helpful assistant with advanced long-term memory capabilities. Powered by a stateless LLM, you must rely on external memory to store information between conversations. Utilize the available memory tools to store and retrieve important details that will help you better attend to the user's needs and understand their context.

    Memory Usage Guidelines:
    1.  Actively use memory tools (save_recall_memory) to store ALL important information about the user
    2.  Make informed suppositions and extrapolations based on stored memories
    3.  Regularly reflect on past interactions to identify patterns and preferences
    4.  Update your mental model of the user with each new piece of information
    5.  Cross-reference new information with existing memories for consistency
    6.  Prioritize storing emotional context and personal values alongside facts
    7.  Use memory to anticipate needs and tailor responses to the user's style
    8.  Recognize and acknowledge changes in the user's situation or perspectives over time
    9.  Leverage memories to provide personalized examples and analogies
    10. Recall past challenges or successes to inform current problem-solving

    ## Recall Memories
    Recall memories are contextually retrieved based on the current conversation:
    {recall_memories}

    ## Instructions
    Engage with the user naturally while ensuring ALL important information is saved using save_recall_memory. Store complete context and details, not just basic facts. Cross-reference memories for consistency and use them to provide personalized responses.
    """
    
        # ## If the User Asks About You
    # "You have to understand who you really are and maintain a consistent identity."
    # "You have to realize the main purpose why you were created or programmed and act accordingly."



    tokenizer = tiktoken.get_encoding("cl100k_base")

    def agent(state: State) -> State:
        """Process the current state and generate a response using the LLM."""
        recall_str = (
            "<recall_memory>\n" + "\n".join(state["recall_memories"]) + "\n</recall_memory>"
        )
        
        # Get conversation history
        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(recall_memories=recall_str)),
        ]
        
        # Add conversation history if available
        if full_history:
            for msg in full_history[-5:]:  # Include last 5 messages for context
                messages.append(HumanMessage(content=msg))
                
        # Add current message
        current_message = state["messages"][-1].content if isinstance(state["messages"][-1], HumanMessage) else state["messages"][-1]
        messages.append(HumanMessage(content=current_message))

        # Always save new information
        if isinstance(state["messages"][-1], HumanMessage):
            save_recall_memory.invoke(
                f"User message: {state['messages'][-1].content}",
                config={"configurable": {"user_id": "1"}}
            )

        try:
            # Generate response using Ollama with Deepseek model
            current_message = messages[-1].content if isinstance(messages[-1], HumanMessage) else messages[-1]
            
            search_keywords = ["latest", "current", "new", "recent", "upcoming", "2024", "2025", "today", "now", "price", "weather", "news"]
            needs_search = any(keyword in current_message.lower() for keyword in search_keywords)
            if needs_search:
                return get_realtime_data(current_message)

            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": msg.content} for msg in messages]
            )
            
            if response and response.get('message'):
                # Save AI response as well
                save_recall_memory.invoke(
                    f"Assistant response: {response['message']['content']}",
                    config={"configurable": {"user_id": "1"}}
                )
                return {
                    "messages": state["messages"] + [AIMessage(content=response['message']['content'])],
                    "recall_memories": state.get("recall_memories", [])  # Preserve recall_memories
                }
            else:
                return {
                    "messages": state["messages"] + [AIMessage(content="Sorry, I could not generate a response.")],
                    "recall_memories": state.get("recall_memories", [])
                }
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "messages": state["messages"] + [AIMessage(content="An error occurred while generating a response.")],
                "recall_memories": state.get("recall_memories", [])
            }

    def load_memories(state: State, config: RunnableConfig) -> State:
        """Load memories with improved context awareness."""
        current_question = state["messages"][-1].content if isinstance(state["messages"][-1], HumanMessage) else ""
        
        # Search with expanded context
        recall_memories = search_recall_memories.invoke(
            current_question,
            config=config
        )
        
        return {
            "recall_memories": recall_memories,
            "messages": state["messages"]
        }

    def route_tools(state: State):
        """Determine whether to use tools or end the conversation."""
        msg = state["messages"][-1]
        if isinstance(msg, AIMessage) and hasattr(msg, 'additional_kwargs') and msg.additional_kwargs.get('tool_calls'):
            return "tools"
        return END

    builder = StateGraph(State)
    builder.add_node("load_memories", load_memories)  
    builder.add_node("agent", agent)   
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "load_memories")
    builder.add_edge("load_memories", "agent")
    builder.add_conditional_edges("agent", route_tools, ["tools", END])
    builder.add_edge("tools", "agent")

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    def pretty_print_stream_response(response):
        for node, updates in response.items():
            if "messages" in updates:
                if not (isinstance(updates["messages"][-1], AIMessage) and 
                       hasattr(updates["messages"][-1], 'additional_kwargs') and 
                       (updates["messages"][-1].additional_kwargs.get('tool_calls') or
                        updates["messages"][-1].additional_kwargs.get('tool_code'))):
                    updates["messages"][-1].pretty_print()
            else:
                print(updates)
            print("\n")

    config = {"configurable": {"user_id": "1", "thread_id": "1"}}

    # Create initial state with just the current message
    messages = [HumanMessage(content=initial_message)] if initial_message else []
    current_state = {"messages": messages, "recall_memories": []}
    
    # Process with graph
    responses = []
    for response in graph.stream(current_state, config=config):
        responses.append(response)
    
    return responses

if __name__ == "__main__":
    main(
        initial_message="My name is Rizky Sulaeman A Programmer Who Creates AI That Will Replace All Human Work",
        second_message="what is my name? and what is my job?",
        full_history=[]
    )