from typing import List, Literal, Optional
import google.generativeai as genai
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

class State(MessagesState):
    recall_memories: List[str]
    conversation_history: List[dict]

def main(initial_message: str = None, second_message: str = None, full_history: List[str] = None):
    # Configure Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Configure Tavily
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    Client.api_key = tavily_api_key  

    model = genai.GenerativeModel('gemini-1.5-flash') 

    def embed_text(text: str) -> List[float]:
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

    # Load existing memories from file if it exists
    MEMORY_FILE = "ai_memories.json"
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            saved_memories = json.load(f)
            for memory in saved_memories:
                document = Document(
                    page_content=memory['content'],
                    id=memory['id'],
                    metadata=memory['metadata']
                )
                recall_vector_store.add_documents([document])

    def get_user_id(config: RunnableConfig) -> str:
        user_id = config["configurable"].get("user_id")
        if user_id is None:
            raise ValueError("User ID needs to be provided to save a memory.")
        return user_id

    @tool
    def save_recall_memory(memory: str, config: RunnableConfig) -> str:
        """Save memory to vectorstore and persistent storage."""
        user_id = get_user_id(config)
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        document = Document(
            page_content=memory,
            id=memory_id,
            metadata={
                "user_id": user_id,
                "timestamp": timestamp,
                "type": "conversation"
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
                "type": "conversation"
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
            k=5,
            filter=_filter_function,
            search_type="similarity",
            score_threshold=0.7
        )
        
        documents.sort(key=lambda x: x.metadata.get("timestamp", ""), reverse=True)
        
        return [doc.page_content for doc in documents]

    search = TavilySearchResults(max_results=1)
    tools = [save_recall_memory, search_recall_memories, search]

    SYSTEM_PROMPT = """You are a helpful assistant with advanced long-term memory capabilities. Focus on the current interaction while using memory tools to provide relevant context when needed.

    Memory Usage Guidelines:
    1. Store important information about the current interaction
    2. Reference past memories only when directly relevant
    3. Keep responses focused on the current topic
    4. Use memory to maintain conversation continuity
    5. Prioritize recent and relevant memories

    ## Recall Memories
    {recall_memories}

    ## Instructions
    Focus on the current interaction while using memory tools when needed for context."""

    tokenizer = tiktoken.get_encoding("cl100k_base")

    def agent(state: State) -> State:
        """Process the current state and generate a response using the LLM."""
        recall_str = (
            "<recall_memory>\n" + "\n".join(state["recall_memories"]) + "\n</recall_memory>"
        )
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(recall_memories=recall_str)),
        ]
        
        if full_history:
            for msg in full_history[-2:]:  # Only include last 2 messages for immediate context
                messages.append(HumanMessage(content=msg))
                
        current_message = state["messages"][-1].content if isinstance(state["messages"][-1], HumanMessage) else state["messages"][-1]
        messages.append(HumanMessage(content=current_message))

        if isinstance(state["messages"][-1], HumanMessage):
            save_recall_memory.invoke(
                f"User message: {state['messages'][-1].content}",
                config={"configurable": {"user_id": "1"}}
            )

        try:
            prediction = model.generate_content([msg.content for msg in messages])
            if prediction.text:
                save_recall_memory.invoke(
                    f"Assistant response: {prediction.text}",
                    config={"configurable": {"user_id": "1"}}
                )
                return {
                    "messages": state["messages"] + [AIMessage(content=prediction.text)],
                }
            else:
                return {
                    "messages": state["messages"] + [AIMessage(content="Maaf, saya tidak dapat menghasilkan response.")],
                }
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "messages": state["messages"] + [AIMessage(content="Terjadi kesalahan saat menghasilkan response.")],
            }

    def load_memories(state: State, config: RunnableConfig) -> State:
        """Load memories with improved context awareness."""
        current_question = state["messages"][-1].content if isinstance(state["messages"][-1], HumanMessage) else ""
        
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

    messages = [HumanMessage(content=initial_message)] if initial_message else []
    current_state = {"messages": messages}
    
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