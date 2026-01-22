import os
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment (supports both OPENROUTER_API_KEY and OPENAI_API_KEY)
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

# Auto-detect provider based on API key format
if API_KEY:
    if API_KEY.startswith("sk-or-v1-"):
        # OpenRouter key
        API_PROVIDER = "openrouter"
        API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
        DEFAULT_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
    elif API_KEY.startswith("sk-"):
        # OpenAI key (starts with sk- but not sk-or-v1-)
        API_PROVIDER = "openai"
        API_BASE_URL = "https://api.openai.com/v1/chat/completions"
        DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    else:
        # Default to OpenRouter if format unknown
        API_PROVIDER = "openrouter"
        API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
        DEFAULT_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
else:
    API_PROVIDER = "openrouter"
    API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.2-3b-instruct:free")

# For backward compatibility
OPENROUTER_API_KEY = API_KEY
OPENROUTER_BASE_URL = API_BASE_URL
LLM_MODEL = DEFAULT_MODEL

# Port configuration - use PORT (provided by hosting) or BACKEND_PORT or default to 8000
BACKEND_PORT = int(os.getenv("PORT") or os.getenv("BACKEND_PORT", 8000))

# CORS origins - support multiple origins separated by commas
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]