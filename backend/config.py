import os
from dotenv import load_dotenv

# Environment Workarounds
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# DYNAMIC PATH RESOLUTION
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)

# Load the .env from the root folder
dotenv_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)

# CONFIGURATION
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
STT_MODEL = os.getenv("STT_MODEL") # NEW: Load the Whisper model name

# Pull folder names from .env
docs_dir_env = os.getenv("DOCS_DIR")
vector_dir_env = os.getenv("VECTORSTORE_DIR")

# Combine paths: Agri_Smart/backend + data/docs
DOCS_PATH = os.path.join(BACKEND_DIR, docs_dir_env) if docs_dir_env else None
VECTORSTORE_PATH = os.path.join(BACKEND_DIR, vector_dir_env) if vector_dir_env else None

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL")

# DEBUGGING
print(f"--- Backend Config Loaded ---")
print(f"Looking for docs in: {DOCS_PATH}")
print(f"Embedding Model: {EMBEDDING_MODEL_NAME}")
print(f"STT Engine: {STT_MODEL}")  # NEW: Added to debug print
print(f"------------------------------")

# AUTO-INITIALIZATION
if DOCS_PATH and VECTORSTORE_PATH:
    os.makedirs(DOCS_PATH, exist_ok=True)
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)