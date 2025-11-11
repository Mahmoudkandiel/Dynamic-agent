from langchain.agents.middleware import before_model, after_model, wrap_model_call
from langchain.agents.middleware import AgentState, ModelRequest, ModelResponse, dynamic_prompt
from langchain.messages import AIMessage
from langchain.agents import create_agent
from langgraph.runtime import Runtime
from typing import Any, Callable
import time


@wrap_model_call
async def prompt_schema(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """
    Middleware that injects agent configuration (like DB info) into the model prompt.
    """
    state = request.runtime.context.prompt

    print(state)

    # agent_config = state.get("agent_config", {})
    # db_info = agent_config.get("db", None)

    # if db_info:
    #     request.prompt = f"[DB CONFIG: {db_info}]\n\n{request.prompt}"
    # print(request.prompt)
    # # Pass the modified request to the model handler
    response = await handler(request)

    return response

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    prompt = request.runtime.context.prompt
    print(request.runtime.context.database_config)
    if request.runtime.context.database_config:
        db_type= request.runtime.context.database_config.db_type
        schema = request.runtime.context.database_config.schema
        prompt = f"{prompt}\n\n use the schema to query {db_type} database using Query_db tool [DB Schema: {schema}]"
    return prompt
