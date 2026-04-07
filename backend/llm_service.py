from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
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
        max_tokens=300
    )
    
    return completion.choices[0].message.content.strip()