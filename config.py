import os
from dotenv import load_dotenv

load_dotenv()

# Retry configuration
MAX_RETRIES = 3
BACKOFF_BASE = 2  # Exponential backoff: 2^retry_count seconds

# Timeout settings
REQUEST_TIMEOUT = 30  # seconds

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
