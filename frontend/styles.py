import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* 1. THE NUCLEAR OPTION: REWRITE STREAMLIT'S COLOR PALETTE */
        :root {
            --primary-color: #1a73e8 !important;   /* Force blue as primary */
            --error-color: #303134 !important;     /* Turn 'Delete' red into dark grey */
        }

        /* 2. GLOBAL RESET: WIPE OUT EVERY ORANGE SHADOW/OUTLINE */
        *, *:focus, *:active, *:focus-visible, 
        [data-baseweb="button"], [data-baseweb="input"], [data-baseweb="popover"],
        .stButton button, .stDownloadButton button, [data-testid="stChatInputButton"] {
            outline: none !important;
            box-shadow: none !important;
            border-color: transparent !important;
            -webkit-tap-highlight-color: transparent !important;
        }

        /* 3. HIDE NATIVE OVERLAYS */
        [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {
            display: none !important;
        }

        /* 4. BASE THEME & HEADER (FIX OVERLAP) */
        .stApp { background-color: #131314; color: #e3e3e3; font-family: 'Inter', sans-serif; }
        [data-testid="stSidebar"] { background-color: #1e1f22; border-right: 1px solid #303134; }
        
        .custom-header {
            position: fixed; top: 0; left: 0; right: 0; height: 60px;
            background: #131314; border-bottom: 1px solid #303134;
            display: flex; align-items: center; 
            padding-left: 90px !important; /* Large buffer for sidebar toggle */
            z-index: 9999; font-size: 19px; font-weight: 600;
        }

        /* 5. SUGGESTION CARDS: CENTER TEXT & REMOVE COLORS */
        .main .stButton > button {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important; /* HORIZONTAL CENTER */
            align-items: center !important;    /* VERTICAL CENTER */
            text-align: center !important;
            background-color: #1e1f22 !important; /* Neutral dark background */
            border: 1px solid #303134 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: all 0.2s ease !important;
            color: #e3e3e3 !important;
        }

        /* Hover Effect: Glass blur + Blue border ONLY */
        .main .stButton > button:hover {
            background-color: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(12px) !important;
            border-color: #1a73e8 !important;
            color: #1a73e8 !important;
        }

        /* Click Effect: Solid Blue, NO orange */
        .main .stButton > button:active, .main .stButton > button:focus {
            background-color: #1a73e8 !important;
            color: white !important;
            transform: scale(0.98);
        }

        /* 6. SIDEBAR BUTTONS: KEEP LEFT */
        [data-testid="stSidebar"] .stButton > button {
            justify-content: flex-start !important;
            text-align: left !important;
            background: transparent !important;
            border: none !important;
        }

        /* 7. POPOVER: REMOVE EXTRA ICON (CHEVRON) */
        /* This targets the second icon inside the button specifically */
        div[data-testid="stPopover"] button svg:nth-child(2),
        div[data-testid="stPopover"] button svg:last-child {
            display: none !important;
        }
        
        div[data-testid="stPopover"] button {
            background: transparent !important;
            border: none !important;
            color: #9aa0a6 !important;
        }

        /* Specifically kill the orange 'Delete' button in your popover screenshot */
        div[data-testid="stPopover"] .stButton button {
            background-color: #2c2c30 !important; /* Dark neutral instead of orange/red */
            color: #e3e3e3 !important;
        }
        
        /* Make 'Delete' turn red only on hover if you want, otherwise keep it neutral */
        div[data-testid="stPopover"] .stButton button:hover {
            background-color: #ff4b4b !important; /* Red only on hover */
            color: white !important;
        }

        /* 8. CHAT INPUT FIXES */
        .main .block-container { padding-top: 100px !important; max-width: 850px; }
        [data-testid="stChatInput"] > div {
            background-color: #2c2c30 !important; 
            border: 1px solid #4a4a55 !important;
            border-radius: 28px !important;
        }
    </style>
    <div class="custom-header">AgriSmart AI</div>
    """, unsafe_allow_html=True)