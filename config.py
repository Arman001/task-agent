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

# Phase 4: Memory configuration
MEMORY_DB_PATH = "agent_memory.db"
SESSION_MEMORY_LIMIT = 10  # Number of tasks to keep in session
TASK_HISTORY_LIMIT = 1000  # Maximum tasks in history
FILE_CACHE_DAYS = 30  # Days to keep file metadata
