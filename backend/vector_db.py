import os
import glob
import numpy as np
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from config import DOCS_PATH, VECTORSTORE_PATH, EMBEDDING_MODEL_NAME

# Initialize Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def load_docs():
    docs = []
    for file_path in glob.glob(f"{DOCS_PATH}/*"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

                # split document into chunks using "---" as separator
                chunks = text.split("\n---")

                for chunk in chunks:
                    chunk = chunk.strip()
                    if len(chunk) > 50:
                        docs.append(
                            Document(
                                page_content=chunk,
                                metadata={"source": os.path.basename(file_path)}
                            )
                        )
        except Exception:
            pass

    return docs

def init_vectorstore():
    documents = load_docs()
    print("Loaded docs:", len(documents))

    if len(documents) > 0:
        return Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=VECTORSTORE_PATH,
            collection_name="agri_docs"
        )
    else:
        return Chroma(
            embedding_function=embedding_model,
            persist_directory=VECTORSTORE_PATH,
            collection_name="agri_docs"
        )

# Instantiate the vectorstore instance
vectorstore = init_vectorstore()

# ABSTRACTION HELPERS FOR MAIN.PY
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def check_similar_cache(user_msg: str, cache_dict: dict, threshold: float = 0.85) -> str:
    """Checks the cache using Hybrid Search (BM25 + Semantic) and returns the matching key if found."""
    if not cache_dict:
        return None
        
    cached_queries = list(cache_dict.keys())
    
    # 1. Semantic Scoring (Context)
    user_embedding = embedding_model.embed_query(user_msg)
    semantic_scores = []
    for cached_q in cached_queries:
        cached_embedding = embedding_model.embed_query(cached_q)
        semantic_scores.append(cosine_similarity(user_embedding, cached_embedding))
        
    # 2. BM25 Scoring (Keyword matching)
    tokenized_corpus = [q.lower().split() for q in cached_queries]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = user_msg.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Normalize BM25 scores (0 to 1 range)
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
    normalized_bm25 = [score / max_bm25 for score in bm25_scores]
    
    # 3. Hybrid Scoring (60% Semantic + 40% BM25)
    best_score = -1
    best_match = None
    
    for i, cached_q in enumerate(cached_queries):
        hybrid_score = (0.6 * semantic_scores[i]) + (0.4 * normalized_bm25[i])
        if hybrid_score > best_score:
            best_score = hybrid_score
            best_match = cached_q
            
    if best_score > threshold:
        return best_match
    return None

def get_relevant_docs(user_msg: str, k: int = 3) -> str:
    """Searches the vector store and returns formatted document text."""
    results = vectorstore.similarity_search_with_score(user_msg, k=k)
    retrieved_docs = "\n\n".join(
        [f"Source: {doc.metadata['source']}\n{doc.page_content}" for doc, score in results]
    )
    return retrieved_docs