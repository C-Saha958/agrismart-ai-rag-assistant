import streamlit as st
import uuid
import random
import base64
from config import SUGGESTIONS_POOL, COPY_ICON, DOWNLOAD_ICON
from storage import load_db, delete_chat, pin_chat, unpin_chat
from export import get_pdf_href

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
    b64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    pdf_href = get_pdf_href(text, f"agri_response_{unique_id}.pdf")
    
    # JavaScript for clipboard with fallback
    js_code = f"""
    const b='{b64_text}';
    const bytes=new Uint8Array(atob(b).split('').map(c=>c.charCodeAt(0)));
    const txt=new TextDecoder('utf-8').decode(bytes);
    const cb=navigator.clipboard;
    const fb=(t)=>{{const a=document.createElement('textarea');a.value=t;a.style.position='fixed';document.body.appendChild(a);a.select();try{{document.execCommand('copy');s();}}catch(e){{}}document.body.removeChild(a);}};
    const s=()=>{{const t=document.getElementById('toast-{unique_id}');if(t){{t.style.opacity=1;setTimeout(()=>t.style.opacity=0,2000);}}}};
    if(cb && window.isSecureContext) cb.writeText(txt).then(s).catch(()=>fb(txt));
    else fb(txt);
    """.replace('\n', '')

    # UI FIX: Added margin-top: 15px and gap for better spacing. 
    # Swapped color to primary blue.
    html = f"""
    <div style="display: flex; align-items: center; margin-top: 15px; gap: 10px;">
        <button onclick="{js_code}" style="background:none; border:none; cursor:pointer; color:#0ea5e9; padding:5px;" title="Copy to Clipboard">
            {COPY_ICON}
        </button>
        <a href="{pdf_href}" download="agri_response.pdf" style="color:#0ea5e9; text-decoration:none; padding:5px;" title="Download PDF">
            {DOWNLOAD_ICON}
        </a>
        <span id="toast-{unique_id}" style="opacity: 0; transition: opacity 0.3s; color: #0284c7; font-size: 13px; font-weight: 500;">Copied!</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

@st.dialog("Search History")
def search_popup():
    search_text = st.text_input("Search", placeholder="Type a keyword...", label_visibility="collapsed")
    db = load_db()
    if search_text:
        st.markdown("<hr style='margin: 10px 0; border-color: #bae6fd;'>", unsafe_allow_html=True)
        found = False
        seen_results = set()
        
        sorted_chats = sorted(db["chats"].items(), key=lambda x: x[1].get("created_at", ""), reverse=True)

        for cid, chat in sorted_chats:
            for m in chat["messages"]:
                if search_text.lower() in m["content"].lower():
                    preview = m['content'][:60] + "..." if len(m['content']) > 60 else m['content']
                    result_signature = f"{chat['title']}_{preview}"
                    
                    if result_signature not in seen_results:
                        seen_results.add(result_signature)
                        found = True
                        if st.button(f"📄 {chat['title']}\n\n{preview}", key=f"search_{cid}", use_container_width=True):
                            load_chat(cid)
                            st.rerun()
                    break 
                    
        if not found: st.caption("No matching messages found in history.")