import streamlit as st
import os
import requests
import ui.admin_view as admin_view
import ui.customer_view as customer_view

st.set_page_config(page_title='OmniAI', layout='wide', page_icon='🤖')

# Custom CSS for Premium Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-color: #0a0a0f;
        --card-bg: rgba(20, 20, 25, 0.7);
        --text-main: #f3f4f6;
        --text-muted: #9ca3af;
        --accent-1: #7c3aed;
        --accent-2: #2563eb;
        --border-color: rgba(255, 255, 255, 0.1);
        --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-color);
        color: var(--text-main);
    }

    .stApp {
        background: radial-gradient(circle at top left, rgba(124, 58, 237, 0.05), transparent 40%),
                    radial-gradient(circle at bottom right, rgba(37, 99, 235, 0.05), transparent 40%);
        background-color: var(--bg-color);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 20, 0.95) !important;
        border-right: 1px solid var(--border-color);
        backdrop-filter: blur(10px);
    }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--glass-shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(124, 58, 237, 0.15);
        border: 1px solid rgba(124, 58, 237, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2)) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
    }

    /* File Uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(124, 58, 237, 0.4);
        border-radius: 12px;
        transition: all 0.3s;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(124, 58, 237, 0.05);
        border-color: var(--accent-1);
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #fff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-weight: 500 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255,255,255,0.03) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: var(--text-muted);
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-main) !important;
        border-bottom-color: var(--accent-1) !important;
    }
    
    /* Chat bubbles */
    .stChatMessage {
        background-color: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Input Box */
    .stChatInput {
        background-color: rgba(20, 20, 25, 0.8) !important;
        border: 1px solid var(--border-color) !important;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def api_request(method, endpoint, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"
    headers = kwargs.pop("headers", {})
    if st.session_state.get("admin_token"):
        headers["X-Admin-Token"] = st.session_state["admin_token"]

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, **kwargs)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {e}")
        return None

# Sidebar Setup
with st.sidebar:
    st.markdown("<h1 class='gradient-text' style='text-align: center; margin-bottom: 30px;'>🤖 OmniAI</h1>", unsafe_allow_html=True)
    
    view_selection = st.radio(
        "Navigation",
        ['🔧 Admin Dashboard', '💬 Customer Chat'],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    
    # Check API health
    health_data = api_request('GET', '/api/health')
    api_status = "🟢 Online" if health_data else "🔴 Offline"
    
    st.markdown(f"**API Backend:** {api_status}")
    st.markdown("**Gemini Models:** 🟢 Ready")
    
    st.markdown("---")
    with st.expander("About OmniAI"):
        st.markdown("""
        **OmniAI E-Commerce Automation**
        
        An intelligent system that automates product cataloging, dynamic pricing, and customer support using Advanced Agentic AI.
        
        Built with FastAPI, Streamlit, and Gemini.
        """)

# Route to appropriate view
if view_selection == '🔧 Admin Dashboard':
    if not st.session_state.get("authenticated", False):
        st.markdown("<div class='glass-card' style='max-width: 400px; margin: 50px auto; text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2 class='gradient-text'>Admin Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-muted);'>Please enter the admin password to access the dashboard.</p>", unsafe_allow_html=True)
        pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Admin Password")
        if st.button("Login", use_container_width=True):
            st.session_state["admin_token"] = pwd
            # Verify by checking a protected route
            if api_request("GET", "/api/analytics") is not None:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.session_state["admin_token"] = ""
                st.error("Invalid password or API offline")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        admin_view.render(api_request)
else:
    customer_view.render(api_request)
