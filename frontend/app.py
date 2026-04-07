# app.py
import streamlit as st
import time
import requests

# Import your custom components (kept for fallback/suggestions)
try:
    from components import apply_css, suggestion_cards
except ImportError:
    pass 

# Import separated modules
from config import API_URL, USER_AVATAR, AI_AVATAR
from styles import apply_custom_css
from storage import load_db, load_cache, save_to_cache, save_message
from ui import init_session_state, new_chat, load_chat, render_action_row, search_popup, options_popup

# -------------------------
# SETUP
# -------------------------
st.set_page_config(page_title="AgriSmart", layout="centered")
apply_custom_css()
init_session_state()

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    if st.button("+ New Chat"): new_chat(); st.rerun()
    if st.button("Search"): search_popup()
    st.markdown("<hr style='margin: 10px 0; border-color: #4d4d4f;'>", unsafe_allow_html=True)
    
    db = load_db()
    
    if db.get("pinned"):
        st.caption("📍 PINNED")
        for cid in reversed(db["pinned"]):
            if cid not in db["chats"]: continue
            row1, row2 = st.columns([8, 2])
            with row1:
                if st.button(db["chats"][cid]["title"], key="pin"+cid): load_chat(cid); st.rerun()
            with row2:
                if st.button("⋮", key="pin_menu"+cid): options_popup(cid)
        st.markdown("<br>", unsafe_allow_html=True)
        
    st.caption("≡ RECENT CHATS")
    for cid, chat in reversed(list(db["chats"].items())):
        if cid in db.get("pinned", []): continue
        row1, row2 = st.columns([8, 2])
        with row1:
            if st.button(chat["title"], key="chat"+cid): load_chat(cid); st.rerun()
        with row2:
            if st.button("⋮", key="recent_menu"+cid): options_popup(cid)

# -------------------------
# MAIN CHAT AREA
# -------------------------
if len(st.session_state.messages) == 0:
    st.markdown("<h1 style='text-align: center; margin-top: 10vh; margin-bottom: 5vh;'>AgriSmart</h1>", unsafe_allow_html=True)
    if not st.session_state.hide_suggestions:
        cols = st.columns(3)
        for i, suggestion in enumerate(st.session_state.suggestions):
            with cols[i]: st.info(suggestion)

for i, m in enumerate(st.session_state.messages):
    avatar_svg = USER_AVATAR if m["role"] == "user" else AI_AVATAR
    with st.chat_message(m["role"], avatar=avatar_svg):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            render_action_row(m["content"], f"hist_{i}")

# -------------------------
# INPUT & API LOGIC
# -------------------------
prompt = st.chat_input("Message Agri AI...")
if prompt:
    st.session_state.hide_suggestions = True
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    title = prompt[:30]
    save_message(st.session_state.chat_id, title, "user", prompt)
    
    with st.chat_message("assistant", avatar=AI_AVATAR):
        message_placeholder = st.empty()
        cache = load_cache()
        clean_prompt = prompt.lower().strip()
        
        if clean_prompt in cache:
            message_placeholder.markdown("*Thinking...*")
            time.sleep(0.3)
            cached_data = cache[clean_prompt]
            answer = cached_data["answer"]
            source = cached_data["source"]
            
            source_lower = str(source).lower()
            if "kb" in source_lower or "knowledge" in source_lower or ".txt" in source_lower or "/" in source_lower:
                display_source = "kb"
                source_text = "From Knowledge Base"
            else:
                display_source = "ai"
                source_text = "AI Generated Answer"
                
            reply = f"**[Cached]**\n\n{answer}\n\n---\n*Source: {source_text}*"
            message_placeholder.markdown(reply)
            
        else:
            message_placeholder.markdown("*Thinking...*")
            time.sleep(0.4)
            try:
                response = requests.post(API_URL, json={"query": prompt, "chat_id": st.session_state.chat_id}, timeout=60)
                message_placeholder.markdown("*Typing...*")
                time.sleep(0.4)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    source = data.get("source", "ai") 
                    
                    source_lower = str(source).lower()
                    if "kb" in source_lower or "knowledge" in source_lower or ".txt" in source_lower or "/" in source_lower:
                        display_source = "kb"
                        source_text = "From Knowledge Base"
                    else:
                        display_source = "ai"
                        source_text = "AI Generated Answer"
                        
                    reply = f"{answer}\n\n---\n*Source: {source_text}*"
                    save_to_cache(prompt, answer, display_source)
                else:
                    reply = f"Backend error {response.status_code}"
            except Exception as e:
                reply = f"Backend offline: {str(e)}"
                
            message_placeholder.markdown(reply)
            
        render_action_row(reply, "live_new")
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message(st.session_state.chat_id, title, "assistant", reply)