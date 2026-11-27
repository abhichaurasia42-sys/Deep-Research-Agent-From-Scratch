"""Configuration settings for the Deep Research Agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LangChain Tracing Configuration
os.environ.pop("LANGCHAIN_TRACING", None)  # Disable deprecated v1 tracer
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Model Configuration
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
DEFAULT_TEMPERATURE = 0

# Research Agent Limits
MAX_RESEARCHER_ITERATIONS = 6  # Max calls to think_tool + ConductResearch
MAX_CONCURRENT_RESEARCHERS = 3  # Max parallel research agents
MAX_CONTEXT_MESSAGES = 12  # Cap messages to avoid oversized requests

# Report Writer Configuration
WRITER_MAX_TOKENS = 8192