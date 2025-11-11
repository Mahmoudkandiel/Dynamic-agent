from dotenv import load_dotenv
from typing import List
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import BaseTool
from schemas.agent import AgentConfig
from .tools import tavily_search, code_interpreter,mongo_query_tool,postgres_query_tool,mysql_query_tool
from .middleware import personalized_prompt
from utils import get_memory
import time

load_dotenv()


TOOLS_REGISTRY = {
    "web_search": tavily_search,
    "code_interpreter":code_interpreter ,
    "mongo_query_tool":mongo_query_tool,
    "postgres_query_tool":postgres_query_tool, 
    "mysql_query_tool":mysql_query_tool,
}


def build_agent(config: AgentConfig):
    """
    Build a LangGraph agent dynamically using an AgentConfig schema.
    """


    print(f"Building agent with tools: {config.tools} and model: {config.model}")
    tools_to_use: List[BaseTool] = [
        TOOLS_REGISTRY[name]
        for name in config.tools
        if name in TOOLS_REGISTRY
    ]
    model = init_chat_model(
        model=config.model,
        # model_provider=config.model_provider,
        temperature=config.temperature,
        configurable_fields=("model", "model_provider"),
    )


    agent = create_agent(
        model=model,
        tools=tools_to_use,
        system_prompt=config.prompt,
        context_schema=AgentConfig,
        checkpointer=get_memory(),
        middleware=[personalized_prompt],
    )
 


    return agent
