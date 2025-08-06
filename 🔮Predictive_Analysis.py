# pages/2_🔮_Predictive_Analysis.py
import streamlit as st
from utils import generate_prediction

st.set_page_config(page_title="Predictive Analysis", page_icon="🔮", layout="wide")
st.title("🔮 Predictive Analysis")

if 'client' not in st.session_state or st.session_state.get('client') is None:
    st.warning("Please configure your AI Provider on the 'Home' page.")
elif 'dfs' not in st.session_state:
    st.info("Please upload a data file on the 'Home' page to use this feature.")
else:
    question = st.text_area("Ask a question about the future...", placeholder="e.g., 'Based on sales trends, what can we expect for the next quarter?'")
    if st.button("Generate Forecast"):
        if question:
            with st.spinner("AI is looking into the future..."):
                client = st.session_state['client']
                provider = st.session_state['provider']
                dfs = st.session_state['dfs']
                prediction = generate_prediction(dfs, question, client, provider)
                st.divider()
                st.header("AI's Forecast")
                st.markdown(prediction)
        else:
            st.error("Please enter a question.")