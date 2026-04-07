# styles.py
import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #343541; color: #ececf1; }
        [data-testid="stSidebar"] { background-color: #202123; border-right: none; }
        header { visibility: hidden; }
        
        .stMarkdown, .stMarkdown p {
            font-size: 15px !important;
            line-height: 1.6 !important;
        }

        .stButton > button {
            width: 100%; text-align: left; border-radius: 6px; padding: 10px 14px;
            background-color: transparent; color: #ececf1; border: none !important;
            box-shadow: none !important; transition: all 0.2s ease;
            justify-content: flex-start; display: block; white-space: nowrap;
            overflow: hidden; text-overflow: ellipsis; font-size: 14px;
        }
        .stButton > button:hover { background-color: #2A2B32 !important; color: #fff; }
        
        [data-testid="stSidebar"] div:first-child > .stButton > button {
            border: 1px solid #565869 !important; margin-bottom: 10px;
        }

        [data-testid="stChatInput"] {
            background-color: #40414f !important; border: none !important;
            border-radius: 12px; box-shadow: 0 0 15px rgba(0,0,0,0.1);
        }
        
        [data-testid="stChatMessage"]:has(#user-avatar-svg) {
            flex-direction: row-reverse;
        }
        [data-testid="stChatMessage"]:has(#user-avatar-svg) [data-testid="stMarkdownContainer"] {
            text-align: right;
            background-color: #40414f;
            padding: 12px 18px;
            border-radius: 18px 18px 4px 18px;
            display: inline-block;
        }
        
        [data-testid="stChatMessage"]:has(#ai-avatar-svg) [data-testid="stMarkdownContainer"] {
            text-align: left;
            padding-top: 5px;
        }

        .flat-icon-btn {
            background: transparent !important; border: none !important;
            color: #8e8ea0 !important; padding: 4px !important; margin-right: 5px;
            cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
            border-radius: 4px; transition: 0.2s;
        }
        .flat-icon-btn:hover { color: #ececf1 !important; background-color: #40414f !important; }
        hr { border-color: #4d4d4f; }
    </style>
    """, unsafe_allow_html=True)