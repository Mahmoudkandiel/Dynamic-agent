AGENT_CONFIG_SPEC = {
    "model_provider": {
        "type": "str",
        "choices": ["azure_openai", "anthropic", "google"],
        "default": "azure_openai",
        "description": "Which provider hosts the model."
    },
    "model": {
        "type": "str",
        "choices_by_provider": {
            "azure_openai": ["azure_openai:gpt-5-nano", "gpt-5" , "gpt-5-mini"],
            "anthropic": ["claude-3", "claude-2.1"],
            "google": ["gemini-1.5", "gemini-pro"]
        },
        "default": "gpt-4",
        "description": "The model name to use."
    },
    "temperature": {
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "default": 0.7,
        "description": "Controls randomness in generation."
    },
    "prompt": {
        "type": "str",
        "default": "You are a helpful assistant.",
        "description": "Base prompt for the agent."
    },
    "tools": {
        "type": "list[str]",
        "choices": ["web_search","code_interpreter","postgres_query_tool","mongo_query_tool","mysql_query_tool"],
        "default": [],
        "description": "Enabled tools for the agent."
    },
    "database_type": {
        "type": "str",
        "choices": ["mongodb", "postgres", "mysql"],
        "default": "mongodb",
        "description": "The type of database to connect to."
    }
}
