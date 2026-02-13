import json


def load_groq_key(file_path: str = None):
    if file_path is None:
        from config import GROQ_API_KEY_FILE
        file_path = GROQ_API_KEY_FILE
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[load_files] Groq API key not found: {file_path}")
        with open(file_path, "w") as f:
            groq_key = input("[load_files] Enter your Groq API key: ")
            json.dump({"groq_key": groq_key}, f)
            return {"groq_key": groq_key}


def load_system_messages(file_path: str = None):
    if file_path is None:
        from config import SYSTEM_MESSAGES_FILE
        file_path = SYSTEM_MESSAGES_FILE
    with open(file_path, 'r') as f:
        return json.load(f)
