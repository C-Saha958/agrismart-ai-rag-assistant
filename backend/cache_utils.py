import numpy as np

# In-memory query cache
query_cache = {}

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))