import google.generativeai as genai
import os
from langchain.agents import AgentExecutor
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
from langchain_core.outputs import ChatGeneration, ChatResult

GEMINI_KEY = os.getenv("GEMINI_KEY", None) 
genai.configure(api_key=GEMINI_KEY)


model = genai.GenerativeModel('gemini-1.5-flash')
config = GenerationConfig(
    temperature=0
)


wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
tavily = TavilySearchResults()
tools = [wikipedia, tavily]


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant that uses tools to find information and answer questions."),
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
        
        response = self.model.generate_content(prompt, generation_config=config)
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

langchain_model = GeminiChatModel(model=model)

from langchain.agents import create_openai_tools_agent
agent = create_openai_tools_agent(langchain_model, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


print("Response without using tools:")
response = model.generate_content("Where Is Indonesia?")
print(response.text)
print("\n" + "="*50 + "\n")


print("Response using tools through agent:")
print(agent_executor.invoke({"input": "Where Is Indonesia?"}))
