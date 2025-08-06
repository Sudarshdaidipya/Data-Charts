# pages/4_📖_Data_Story.py
import streamlit as st
from utils import generate_story, answer_story_question

st.set_page_config(page_title="Data Story", page_icon="📖", layout="wide")
st.title("📖 AI-Generated Data Story")

if 'client' not in st.session_state or st.session_state.get('client') is None:
    st.warning("Please configure your AI Provider on the 'Home' page.")
elif 'dfs' not in st.session_state:
    st.info("Please upload a data file on the 'Home' page to use this feature.")
else:
    client = st.session_state['client']
    provider = st.session_state['provider']
    dfs = st.session_state['dfs']
    
    # Generate and display the story
    with st.spinner("AI is crafting your data story..."):
        # Store the story in session state to use it as context for follow-up questions
        if 'data_story' not in st.session_state:
            st.session_state['data_story'] = generate_story(dfs, client, provider)
        
        st.markdown(st.session_state['data_story'])

    st.divider()

    # --- NEW: Question box for the data story ---
    st.subheader("❓ Ask a Follow-up Question")
    
    user_question = st.text_area("Your question about this story:", key="story_q")

    if st.button("Get Answer", key="story_q_button"):
        if user_question:
            with st.spinner("AI is thinking..."):
                # Retrieve the story from session state to provide context
                data_story_context = st.session_state.get('data_story', '')
                
                answer = answer_story_question(data_story_context, user_question, dfs, client, provider)
                
                st.info(answer)
        else:
            st.warning("Please enter a question.")