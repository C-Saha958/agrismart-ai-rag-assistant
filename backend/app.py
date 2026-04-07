import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest
from database import init_db, create_new_chat, save_message
from cache_utils import query_cache
from vector_db import check_similar_cache, get_relevant_docs
from llm_service import get_llm_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.get("/")
def health():
    return {"status": "online"}

@app.post("/chat")
def chat_endpoint(data: ChatRequest):
    user_msg = data.query.strip()
    chat_id = data.chat_id or ""

    if not user_msg:
        return {"answer": "Please type message", "chat_id": chat_id}

    # New Chat Logic
    if chat_id == "":
        chat_id = str(uuid.uuid4())
        title = " ".join(user_msg.split()[:6])
        create_new_chat(chat_id, title)

    save_message(chat_id, "user", user_msg)

    # 1. Exact Cache Check
    if user_msg in query_cache:
        return {"answer": query_cache[user_msg], "chat_id": chat_id, "source": "cache"}

    # 2. Semantic Cache Check
    similar_query_key = check_similar_cache(user_msg, query_cache)
    if similar_query_key:
        return {"answer": query_cache[similar_query_key], "chat_id": chat_id, "source": "cache"}

    # 3. Knowledge Base Retrieval
    retrieved_docs = get_relevant_docs(user_msg)

    # 4. LLM Response (Model name hidden inside the service)
    raw_answer = get_llm_answer(user_msg, retrieved_docs)

    # 5. Parsing & Source Attribution
    if "[SOURCE:KB]" in raw_answer:
        source, answer = "Knowledge Base", raw_answer.replace("[SOURCE:KB]", "").strip()
    elif "[SOURCE:AI]" in raw_answer:
        source, answer = "AI Generated Answer", raw_answer.replace("[SOURCE:AI]", "").strip()
    else:
        source, answer = "AI Generated Answer", raw_answer

    # 6. Finalize
    query_cache[user_msg] = answer
    save_message(chat_id, "bot", answer)

    return {"answer": answer, "chat_id": chat_id, "source": source}