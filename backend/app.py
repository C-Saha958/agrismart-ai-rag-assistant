import uuid
import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import ChatRequest
from database import init_db, create_new_chat, save_message
from cache_utils import query_cache, save_cache
from vector_db import check_similar_cache, get_relevant_docs
from llm_service import get_llm_answer, transcribe_audio

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

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """Receives audio file from frontend and returns Whisper transcription."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(await file.read())
            temp_audio_path = temp_audio.name
            
        text = transcribe_audio(temp_audio_path)
        os.remove(temp_audio_path)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}

# NEW ENDPOINT: Auto-generate chat titles via LLM
class TitleRequest(BaseModel):
    query: str

@app.post("/generate_title")
def generate_title_endpoint(data: TitleRequest):
    try:
        from llm_service import client
        from config import GROQ_MODEL
        # Direct LLM call for a super quick summary
        prompt = f"Give a short 3 to 4 word title for this prompt: '{data.query}'. Reply ONLY with the title, no quotes, no extra formatting."
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=15
        )
        title = completion.choices[0].message.content.strip().strip('"').strip("'")
        return {"title": title}
    except Exception as e:
        return {"title": data.query[:30] + "..."}

@app.post("/chat")
def chat_endpoint(data: ChatRequest):
    user_msg = data.query.strip()
    chat_id = data.chat_id or ""

    if not user_msg:
        return {"answer": "Please type message", "chat_id": chat_id}

    if chat_id == "":
        chat_id = str(uuid.uuid4())
        title = " ".join(user_msg.split()[:6])
        create_new_chat(chat_id, title)

    save_message(chat_id, "user", user_msg)

    if user_msg in query_cache:
        return {"answer": query_cache[user_msg], "chat_id": chat_id, "source": "From Database (Cache)"}

    similar_query_key = check_similar_cache(user_msg, query_cache)
    if similar_query_key:
        return {"answer": query_cache[similar_query_key], "chat_id": chat_id, "source": "From Database (Cache)"}

    retrieved_docs = get_relevant_docs(user_msg)
    raw_answer = get_llm_answer(user_msg, retrieved_docs)

    # EXACT MATCH TO USER REQUIREMENTS
    if "[SOURCE:KB]" in raw_answer:
        source = "From Database"
        answer = raw_answer.replace("[SOURCE:KB]", "").strip()
    elif "[SOURCE:AI]" in raw_answer:
        source = "AI Generated Answer"
        answer = raw_answer.replace("[SOURCE:AI]", "").strip()
    else:
        source = "AI Generated Answer"
        answer = raw_answer

    query_cache[user_msg] = answer
    save_cache(query_cache)
    save_message(chat_id, "bot", answer)

    return {"answer": answer, "chat_id": chat_id, "source": source}