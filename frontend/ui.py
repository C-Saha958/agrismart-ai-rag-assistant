# ui.py
import streamlit as st
import uuid
import random
import urllib.parse
from config import SUGGESTIONS_POOL, COPY_ICON, DOWNLOAD_ICON
from storage import load_db, delete_chat, pin_chat, unpin_chat
from export import get_pdf_href, export_chat_pdf

def init_session_state():
    if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
    if "messages" not in st.session_state: st.session_state.messages = []
    if "suggestions" not in st.session_state: st.session_state.suggestions = random.sample(SUGGESTIONS_POOL, 3)
    if "hide_suggestions" not in st.session_state: st.session_state.hide_suggestions = False

def new_chat():
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.hide_suggestions = False
    st.session_state.suggestions = random.sample(SUGGESTIONS_POOL, 3)

def load_chat(cid):
    db = load_db()
    st.session_state.chat_id = cid
    st.session_state.messages = db["chats"][cid]["messages"]
    st.session_state.hide_suggestions = True

def render_action_row(text, unique_id):
    encoded_text = urllib.parse.quote(text)
    pdf_href = get_pdf_href(text, f"agri_response_{unique_id}.pdf")
    html = f"""
    <div style="display: flex; align-items: center; margin-top: 5px;">
        <button onclick='
            try {{
                const txt = decodeURIComponent("{encoded_text}");
                navigator.clipboard.writeText(txt).then(() => {{
                    document.getElementById("toast-{unique_id}").style.opacity=1; 
                    setTimeout(()=>document.getElementById("toast-{unique_id}").style.opacity=0, 2000);
                }});
            }} catch(e) {{ console.error("Copy failed", e); }}
        ' class="flat-icon-btn" title="Copy">
            {COPY_ICON}
        </button>
        <a href="{pdf_href}" download="agri_response.pdf" class="flat-icon-btn" title="Download PDF">
            {DOWNLOAD_ICON}
        </a>
        <span id="toast-{unique_id}" style="opacity: 0; transition: opacity 0.3s; color: #8e8ea0; font-size: 12px; margin-left: 5px;">Copied!</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

@st.dialog("Search History")
def search_popup():
    search_text = st.text_input("Search your chats", placeholder="Type a keyword...", label_visibility="collapsed")
    db = load_db()
    if search_text:
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        found = False
        displayed_chats = set()
        result_counter = 0
        
        for cid, chat in reversed(list(db["chats"].items())):
            for m in chat["messages"]:
                if search_text.lower() in m["content"].lower():
                    if cid not in displayed_chats:
                        found = True
                        preview = m['content'][:40] + "..." if len(m['content']) > 40 else m['content']
                        if st.button(f"**{chat['title']}**\n\n*{preview}*", key=f"search_btn_{cid}_{result_counter}"):
                            load_chat(cid)
                            st.rerun()
                        displayed_chats.add(cid)
                        result_counter += 1
        if not found: st.caption("No matching messages found.")

@st.dialog("⚙ Chat Options")
def options_popup(cid):
    db = load_db()
    chat = db["chats"].get(cid)
    if not chat: return
    st.markdown(f"**{chat['title']}**")
    if cid in db.get("pinned", []):
        if st.button("✕ Unpin Chat", use_container_width=True): unpin_chat(cid); st.rerun()
    else:
        if st.button("📍 Pin Chat", use_container_width=True): pin_chat(cid); st.rerun()
    
    buffer = export_chat_pdf(cid)
    st.download_button("⤓ Download as PDF", data=buffer, file_name=f"{chat['title'][:15]}.pdf", mime="application/pdf", use_container_width=True)
    
    if st.button("✕ Delete Chat", type="primary", use_container_width=True):
        delete_chat(cid)
        if st.session_state.chat_id == cid: new_chat()
        st.rerun()