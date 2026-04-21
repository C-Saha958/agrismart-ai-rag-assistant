import os
import streamlit as st
import requests
from datetime import datetime
from collections import defaultdict
import streamlit.components.v1 as components

# 1. INITIAL SETUP
try:
    from config import API_URL, USER_AVATAR, AI_AVATAR, MIC_SVG, LOAD_SVG
    from styles import apply_custom_css
    from storage import load_db, save_message, pin_chat, unpin_chat, delete_chat
    from export import export_chat_pdf
    from ui import init_session_state, new_chat, load_chat, render_action_row, search_popup
except ImportError:
    st.error("Error: Project modules (config, storage, ui) are missing.")

st.set_page_config(page_title="AgriSmart AI", layout="wide", initial_sidebar_state="expanded") 
init_session_state()
apply_custom_css() 

# 2. FLOATING MIC LOGIC
TRANSCRIBE_URL = API_URL.replace('/chat','/transcribe') if API_URL and '/chat' in API_URL else "http://localhost:8000/transcribe"

components.html(f"""
    <script>
        const parentDoc = window.parent.document;
        const oldMic = parentDoc.getElementById('agri-floating-mic');
        if (oldMic) oldMic.remove();
        const oldStyle = parentDoc.getElementById('agri-mic-style');
        if (oldStyle) oldStyle.remove();

        const style = parentDoc.createElement('style');
        style.id = 'agri-mic-style';
        style.innerHTML = `
            #agri-floating-mic {{
                position: fixed; bottom: 95px; right: 30px; z-index: 99999999;
                cursor: grab; display: flex; align-items: center; justify-content: center;
                user-select: none;
            }}
            #agri-floating-mic:active {{ cursor: grabbing; }}
            .agri-mic-btn {{
                width: 48px; height: 48px; border-radius: 50%;
                background: #1e1f22; border: 1px solid #444746;
                display: flex; align-items: center; justify-content: center;
                transition: transform 0.2s, background 0.2s; color: #9aa0a6;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            }}
            .agri-mic-btn:hover {{ background: #2e2f33; color: #e3e3e3; }}
            .agri-recording {{
                background: #e8eaed !important; color: #131314 !important;
                animation: agri-pulse 1.5s infinite;
            }}
            @keyframes agri-pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(232, 234, 237, 0.4); }}
                70% {{ box-shadow: 0 0 0 12px rgba(232, 234, 237, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(232, 234, 237, 0); }}
            }}
        `;
        parentDoc.head.appendChild(style);

        const micDiv = parentDoc.createElement('div');
        micDiv.id = 'agri-floating-mic';
        micDiv.innerHTML = `<div class="agri-mic-btn" id="agri-mBtn">{MIC_SVG}</div>`;
        parentDoc.body.appendChild(micDiv);

        let savedX = sessionStorage.getItem('agriMicX');
        let savedY = sessionStorage.getItem('agriMicY');
        if (savedX && savedY) {{
            micDiv.style.left = savedX; micDiv.style.top = savedY;
            micDiv.style.right = 'auto'; micDiv.style.bottom = 'auto';
        }}

        const btn = parentDoc.getElementById('agri-mBtn');
        let isDragging = false, isRecording = false;

        micDiv.onmousedown = (e) => {{
            isDragging = false;
            let startX = e.clientX, startY = e.clientY;
            let rect = micDiv.getBoundingClientRect();
            micDiv.style.left = rect.left + 'px'; micDiv.style.top = rect.top + 'px';
            micDiv.style.right = 'auto'; micDiv.style.bottom = 'auto';

            const onMouseMove = (moveEvent) => {{
                isDragging = true;
                micDiv.style.left = (rect.left + moveEvent.clientX - startX) + 'px';
                micDiv.style.top = (rect.top + moveEvent.clientY - startY) + 'px';
            }};

            const onMouseUp = () => {{
                parentDoc.removeEventListener('mousemove', onMouseMove);
                parentDoc.removeEventListener('mouseup', onMouseUp);
                if (isDragging) {{
                    sessionStorage.setItem('agriMicX', micDiv.style.left);
                    sessionStorage.setItem('agriMicY', micDiv.style.top);
                }}
            }};
            parentDoc.addEventListener('mousemove', onMouseMove);
            parentDoc.addEventListener('mouseup', onMouseUp);
        }};

        btn.onclick = async () => {{
            if (isDragging || isRecording) return;
            isRecording = true;
            btn.classList.add('agri-recording');
            btn.innerHTML = `{LOAD_SVG}`;
            
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{audio: true}});
                const mediaRecorder = new MediaRecorder(stream);
                const chunks = [];
                mediaRecorder.ondataavailable = e => chunks.push(e.data);
                mediaRecorder.onstop = async () => {{
                    const blob = new Blob(chunks, {{type: 'audio/webm'}});
                    const fd = new FormData();
                    fd.append("file", blob, "audio.webm");
                    try {{
                        const res = await fetch("{TRANSCRIBE_URL}", {{ method: "POST", body: fd }});
                        const data = await res.json();
                        const chatInput = parentDoc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                        if (chatInput && data.text) {{
                            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                            const newVal = chatInput.value.trim() ? chatInput.value.trim() + " " + data.text.trim() : data.text.trim();
                            nativeSetter.call(chatInput, newVal);
                            chatInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    }} catch (e) {{ console.error("Mic error:", e); }}
                    finally {{
                        btn.classList.remove('agri-recording');
                        btn.innerHTML = `{MIC_SVG}`;
                        isRecording = false;
                        stream.getTracks().forEach(t => t.stop());
                    }}
                }};
                mediaRecorder.start();
                setTimeout(() => {{ if(mediaRecorder.state === "recording") mediaRecorder.stop(); }}, 6000);
            }} catch(e) {{
                alert("Microphone access required.");
                btn.classList.remove('agri-recording');
                btn.innerHTML = `{MIC_SVG}`;
                isRecording = false;
            }}
        }};
    </script>
""", height=0)

# 3. SIDEBAR LOGIC
with st.sidebar:
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    
    if st.button("New Chat", icon=":material/add:", use_container_width=True):
        new_chat()
        st.rerun()
    
    if st.button("Search", icon=":material/search:", use_container_width=True):
        search_popup()

    db = load_db()
    chats = db.get("chats", {})
    pinned_ids = db.get("pinned", [])

    def render_sidebar_chat(cid, chat, is_pinned):
        row_c1, row_c2 = st.columns([85, 15], vertical_alignment="center")
        with row_c1:
            if st.button(chat["title"], key=f"btn_{cid}", use_container_width=True):
                load_chat(cid)
                st.rerun()
        with row_c2:
            with st.popover("", icon=":material/more_vert:", use_container_width=True):
                if is_pinned:
                    if st.button("Unpin", icon=":material/keep_off:", key=f"unpin_{cid}", use_container_width=True):
                        unpin_chat(cid); st.rerun()
                else:
                    if st.button("Pin", icon=":material/push_pin:", key=f"pin_{cid}", use_container_width=True):
                        pin_chat(cid); st.rerun()
                
                buffer = export_chat_pdf(cid)
                st.download_button("Download", data=buffer, file_name=f"{chat['title'][:15]}.pdf", mime="application/pdf", key=f"dl_{cid}", use_container_width=True, icon=":material/download:")
                
                if st.button("Delete", type="primary", icon=":material/delete:", key=f"del_{cid}", use_container_width=True):
                    delete_chat(cid)
                    if st.session_state.chat_id == cid: new_chat()
                    st.rerun()

    pinned_list = []
    for cid in pinned_ids:
        if cid in chats:
            dt_str = chats[cid].get("created_at", "1970-01-01 00:00:00")
            pinned_list.append((cid, chats[cid], dt_str))

    pinned_list.sort(key=lambda x: x[2], reverse=True)

    if pinned_list:
        st.caption("Pinned")
        for cid, chat, _ in pinned_list:
            render_sidebar_chat(cid, chat, is_pinned=True)

    month_groups = defaultdict(list)
    for cid, chat in chats.items():
        if cid not in pinned_ids:
            dt_str = chat.get("created_at", "1970-01-01 00:00:00")
            try:
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                month_key = dt_obj.strftime("%Y-%m")
                month_label = dt_obj.strftime("%B %Y")
            except:
                month_key = "0000-00"
                month_label = "Older"
            month_groups[(month_key, month_label)].append((cid, chat, dt_str))

    sorted_groups = sorted(month_groups.keys(), key=lambda x: x[0], reverse=True)
    for key in sorted_groups:
        st.caption(key[1])
        month_chats = sorted(month_groups[key], key=lambda x: x[2], reverse=True)
        for cid, chat, _ in month_chats:
            render_sidebar_chat(cid, chat, is_pinned=False)

# 4. MAIN CHAT INTERFACE
if not st.session_state.messages:
    st.markdown("<h2 style='text-align: center; margin-top: 15vh; color: #e3e3e3; font-weight: 400;'>How can I help you today?</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, text in enumerate(st.session_state.suggestions):
        with cols[i]:
            if st.button(text, icon=":material/chat_bubble:", key=f"sug_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()

for i, msg in enumerate(st.session_state.messages):
    avatar = USER_AVATAR if msg["role"] == "user" else AI_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            render_action_row(msg["content"], f"row_{i}")

# 5. CHAT INPUT & PROCESSING
prompt = st.chat_input("Ask AgriSmart AI...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]
    if not last_msg.get("processed"):
        user_query = last_msg["content"]
        with st.chat_message("assistant", avatar=AI_AVATAR):
            status = st.empty()
            status.markdown("*(Consulting data...)*")
            try:
                res = requests.post(API_URL, json={"query": user_query, "chat_id": st.session_state.chat_id}, timeout=45)
                if res.status_code == 200:
                    data = res.json()
                    full_resp = f"{data.get('answer', '')}\n\n**Source:** *{data.get('source', 'Knowledge Base')}*"
                else: 
                    full_resp = "Backend error connecting to data source."
            except Exception as e: 
                full_resp = f"Connection failed. Please check your network."
            
            status.markdown(full_resp)
            render_action_row(full_resp, "latest")
            
        st.session_state.messages.append({"role": "assistant", "content": full_resp})
        st.session_state.messages[-2]["processed"] = True 
        save_message(st.session_state.chat_id, user_query[:30], "user", user_query)
        save_message(st.session_state.chat_id, user_query[:30], "assistant", full_resp)
        st.rerun()