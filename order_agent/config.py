import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Initialize Tavily Search Tool
tavily_search = TavilySearchResults(max_results=2)