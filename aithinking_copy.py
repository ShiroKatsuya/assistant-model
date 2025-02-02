import google.generativeai as genai
import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from google.generativeai.types import GenerationConfig
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Optional
from pydantic import BaseModel
from langchain_core.outputs import ChatGeneration, ChatResult, Generation, LLMResult
from langchain_ollama import OllamaLLM

# Configure Gemini
GEMINI_KEY = os.getenv("GEMINI_KEY", None)
genai.configure(api_key=GEMINI_KEY)

# Initialize models
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
calista_model = OllamaLLM(model="calista:latest")

gemini_config = GenerationConfig(
    temperature=0
)

# Tools setup
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
tavily = TavilySearchResults()
tools = [wikipedia, tavily]

# Prompts
general_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant that uses tools to find information and answer questions."),
    ("human", "{input}"),
    ("human", "This is the result of using tools to help you: {agent_scratchpad}")
])

coding_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert programming assistant focused on providing accurate code solutions."),
    ("human", "{input}"),
    ("human", "This is the result of using tools to help you: {agent_scratchpad}")
])

class GeminiChatModel(BaseChatModel, BaseModel):
    model: Any
    verbose: bool = True
    callbacks: Optional[Any] = None
    tags: Optional[List[str]] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, model: Any, **kwargs):
        super().__init__(model=model, **kwargs)
        
    def _generate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt = ""
        for message in messages:
            if isinstance(message, SystemMessage):
                prompt += f"System: {message.content}\n"
            elif isinstance(message, HumanMessage):
                prompt += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                prompt += f"Assistant: {message.content}\n"
        
        response = self.model.generate_content(prompt, generation_config=gemini_config)
        message = AIMessage(content=response.text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "gemini"

    @property
    def _identifying_params(self) -> dict:
        return {"model": "gemini"}

    @property
    def _input_keys(self) -> List[str]:
        return ["input"]

def is_coding_question(question: str) -> bool:
    coding_keywords = [
        "code", "programming", "function", "algorithm", "debug",
        "python", "javascript", "java", "c++", "html", "css",
        "api", "database", "sql", "framework", "library",
        "error", "bug", "compile", "syntax", "implementation"
    ]
    return any(keyword in question.lower() for keyword in coding_keywords)

def get_appropriate_agent(question: str):
    if is_coding_question(question):
        agent = create_openai_tools_agent(calista_model, tools, coding_prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)
    else:
        gemini_chat_model = GeminiChatModel(model=gemini_model)
        agent = create_openai_tools_agent(gemini_chat_model, tools, general_prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

# Example usage
def get_response(question: str):
    agent_executor = get_appropriate_agent(question)
    return agent_executor.invoke({"input": question})

# Test examples
# coding_question = "How do I implement a binary search tree in Python?"
general_question = "html code helllo world"

print("Response for coding question:")
# print(get_response(coding_question))
print("\n" + "="*50 + "\n")

print("Response for general question:")
print(get_response(general_question))