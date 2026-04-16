import numpy as np
import json
import os

CACHE_FILE = "backend_semantic_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_dict, f, indent=2, ensure_ascii=False)

# In-memory query cache loaded from persistent file
query_cache = load_cache()

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))