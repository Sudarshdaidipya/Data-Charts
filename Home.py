# Home.py
import streamlit as st
import pandas as pd
from utils import get_client
import os

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🧠",
    layout="wide"
)

# --- Dark Theme CSS for "Data Analyst" Look ---
dark_theme_css = """
<style>
[data-testid="stAppViewContainer"] > .main { background-color: #0f1116; }
[data-testid="stSidebar"] > div:first-child { background-color: #1c1e24; border-right: 1px solid #3b82f6; }
p, .st-emotion-cache-16txtl3, label, .st-emotion-cache-1y4p8pa, .st-emotion-cache-1q8dd3e { color: #FFFFFF; }
h1, h2, h3 { color: #3b82f6; }
.stButton > button { border-color: #3b82f6; color: #3b82f6; }
.stButton > button:hover { border-color: #FFFFFF; color: #FFFFFF; background-color: #3b82f6; }
</style>
"""
st.markdown(dark_theme_css, unsafe_allow_html=True)

# --- Information about AI Providers ---
PROVIDER_INFO = {
    "Groq": {
        "benefits": "⚡ **Extremely Fast:** Best for real-time applications where speed is critical.",
        "limits": "✅ **Generous Free Tier:** High rate limits suitable for development and small projects.",
        "link": "https://console.groq.com/keys"
    },
    "Google Gemini": {
        "benefits": "🧠 **Advanced Reasoning:** Excellent for complex tasks and multi-modal inputs.",
        "limits": "✅ **Good Free Tier:** Provides a solid number of free requests per minute.",
        "link": "https://aistudio.google.com/app/apikey"
    },
    "OpenAI": {
        "benefits": "🏆 **Industry Standard:** Powerful models like GPT-4o known for their reliability.",
        "limits": "⚠️ **Limited Free Trial:** New accounts get a small free credit which expires.",
        "link": "https://platform.openai.com/api-keys"
    }
}

# --- Sidebar ---
with st.sidebar:
    st.header("🧠 AI Configuration")
    
    selected_provider = st.selectbox(
        "Choose your AI Provider",
        options=list(PROVIDER_INFO.keys())
    )
    
    with st.expander("Provider Details", expanded=True):
        st.markdown(f"**Benefits:** {PROVIDER_INFO[selected_provider]['benefits']}")
        st.markdown(f"**Free Tier:** {PROVIDER_INFO[selected_provider]['limits']}")
        st.link_button("Get API Key Here", PROVIDER_INFO[selected_provider]['link'])

    api_key = st.text_input(f"Enter your {selected_provider} API Key", type="password")
    
    if api_key:
        client, error = get_client(selected_provider, api_key)
        if error:
            st.error(error)
            st.session_state['client'] = None
        else:
            st.session_state['client'] = client
            st.session_state['provider'] = selected_provider
            st.success(f"{selected_provider} client initialized successfully!")
    
    st.divider()
    
    st.header("📁 Your Data")
    # BADLAAV #1: File uploader me 'csv' bhi add kiya gaya
    uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        try:
            # BADLAAV #2: File type ke hisaab se data read karne ki logic
            file_extension = os.path.splitext(uploaded_file.name)[1]
            if file_extension == ".xlsx":
                dfs = pd.read_excel(uploaded_file, sheet_name=None)
            elif file_extension == ".csv":
                df = pd.read_csv(uploaded_file)
                # CSV me sheet nahi hoti, to hum file ke naam ko hi sheet ka naam maan lenge
                sheet_name = os.path.splitext(uploaded_file.name)[0]
                dfs = {sheet_name: df}

            st.session_state['dfs'] = dfs
            st.session_state['original_dfs'] = dfs.copy()
            st.success("✅ File uploaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")

# --- Main Page Layout ---
st.title("🧠 Multi-AI Data Analyst")
st.markdown("Your intelligent assistant, powered by the AI of your choice.")

if 'client' not in st.session_state or st.session_state.get('client') is None:
    st.warning("Please configure your chosen AI provider's API key in the sidebar to begin.")

st.divider()
st.header("How to Get Started")
st.markdown("""
1.  **Choose AI Provider**: Sidebar me apna pasandeeda AI provider chunein.
2.  **Enter API Key**: Usi ke neeche, us provider ka API key daalein.
3.  **Upload Your Data**: API key set hone ke baad, apna Excel ya CSV file upload karein.
4.  **Explore the Pages**: Baaki pages par jaakar analysis karein!
""")