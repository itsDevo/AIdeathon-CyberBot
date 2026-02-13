import pyprojroot

from utils.load_files import load_groq_key, load_system_messages

# Base directory
BASE_DIR = pyprojroot.here()  # This is the root of the project, detected automatically

# Directories
UTILS_DIR = BASE_DIR / "utils"

# Files
GROQ_API_KEY_FILE = BASE_DIR / ".api_keys.json"
SYSTEM_MESSAGES_FILE = UTILS_DIR / "system_messages.json"

# LLM settings
GROQ_API_URL = "https://api.groq.com/openai/v1"
GROQ_LLAMA3_1_70B = "llama-3.1-70b-versatile"
GROQ_LLAMA3_2_90B = "llama-3.2-90b-text-preview"

# Variables
GROQ_API_KEY = load_groq_key()["groq_key"]
SYSTEM_MESSAGES = load_system_messages()
