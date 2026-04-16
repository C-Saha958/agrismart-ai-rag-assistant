from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, STT_MODEL # NEW: Imported the whisper model
from prompts import get_agri_prompt

client = Groq(api_key=GROQ_API_KEY)

def get_llm_answer(user_msg: str, retrieved_docs: str) -> str:
    """Sends the prompt to Groq and returns the raw completion."""
    
    # Get the structured prompt from the prompts file
    full_prompt = get_agri_prompt(user_msg, retrieved_docs)

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3,
        max_tokens=1024 
    )
    
    return completion.choices[0].message.content.strip()

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes an audio file into a text string."""
    with open(audio_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file_path, file.read()),
            model=STT_MODEL, # NEW: Using the variable instead of hardcoded string
            response_format="text",
        )
        return transcription