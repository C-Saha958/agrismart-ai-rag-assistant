import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

JSON_FILE = "chats.json"
CACHE_FILE = "answer_cache.json"

SUGGESTIONS_POOL = [
    "Best crops for monsoon",
    "Tomato leaf disease treatment",
    "Fertilizer for paddy",
    "धान की खेती कैसे करें",
    "Rice disease solution",
    "Market price of wheat"
]

USER_AVATAR = '''<svg id="user-avatar-svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e3e3e3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'''
AI_AVATAR = '''<svg id="ai-avatar-svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1a73e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>'''
COPY_ICON = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'''
DOWNLOAD_ICON = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" x1="15" x2="12" y2="3"></line></svg>'''

MIC_SVG = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:24px;height:24px;"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" x1="12" y1="19" y2="22"></line></svg>'''
LOAD_SVG = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:24px;height:24px;"><path d="M12 22v-4"></path><path d="M12 6V2"></path><path d="M22 12h-4"></path><path d="M6 12H2"></path><path d="M19.07 4.93l-2.83 2.83"></path><path d="M7.76 16.24l-2.83 2.83"></path><path d="M19.07 19.07l-2.83-2.83"></path><path d="M7.76 7.76l-2.83-2.83"></path></svg>'''