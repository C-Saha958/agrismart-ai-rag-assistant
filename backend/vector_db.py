import os
import glob
import numpy as np
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
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

# ===============================
# ABSTRACTION HELPERS FOR MAIN.PY
# ===============================
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def check_similar_cache(user_msg: str, cache_dict: dict, threshold: float = 0.90) -> str:
    """Checks the cache for semantically similar questions and returns the matching key if found."""
    if not cache_dict:
        return None
        
    user_embedding = embedding_model.embed_query(user_msg)
    for cached_q in cache_dict:
        cached_embedding = embedding_model.embed_query(cached_q)
        similarity = cosine_similarity(user_embedding, cached_embedding)
        if similarity > threshold:
            return cached_q
    return None

def get_relevant_docs(user_msg: str, k: int = 3) -> str:
    """Searches the vector store and returns formatted document text."""
    results = vectorstore.similarity_search_with_score(user_msg, k=k)
    retrieved_docs = "\n\n".join(
        [f"Source: {doc.metadata['source']}\n{doc.page_content}" for doc, score in results]
    )
    return retrieved_docs