from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["TAVILY_API_KEY"] = "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"
tavily_search = TavilySearch(
    max_results=5,
    topic="general",
)