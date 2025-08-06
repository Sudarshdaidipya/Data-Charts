# pages/3_📊_Dashboard.py
import streamlit as st
from utils import analyze_data, generate_chart_code, execute_code

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Automated Data Dashboard")

if 'client' not in st.session_state or st.session_state.get('client') is None:
    st.warning("Please configure your AI Provider on the 'Home' page.")
elif 'dfs' not in st.session_state:
    st.info("Please upload a data file on the 'Home' page to see your dashboard.")
else:
    dfs = st.session_state['dfs']
    client = st.session_state['client']
    provider = st.session_state['provider']

    with st.container(border=True):
        st.subheader("🤖 Create Your Own Chart with AI")
        prompt = st.text_area("Describe the chart you want to create...", placeholder="Example: 'Create a pie chart showing sales per region.'")
        if st.button("Generate Chart"):
            if prompt:
                with st.spinner("AI is building your chart..."):
                    code, err = generate_chart_code(dfs, prompt, client, provider)
                    if err: st.error(err)
                    else:
                        figs, err = execute_code(code, dfs)
                        if err:
                            st.error(f"Execution Error: {err}")
                            st.code(code, language="python")
                        elif figs:
                            st.success("Chart generated successfully!")
                            for fig in figs: st.pyplot(fig)
                            with st.expander("View Generated Code"): st.code(code, language="python")
                        else: st.warning("AI did not generate a valid chart. Please try rephrasing.")
            else: st.warning("Please enter a description for the chart.")

    st.divider()
    st.markdown("### Automatically Generated Insights")
    all_insights = analyze_data(dfs)
    for sheet_name, insights in all_insights.items():
        st.header(f"Insights for Sheet: '{sheet_name}'")
        visualizations = insights.get('visualizations', [])
        if not visualizations:
            st.info(f"No standard visualizations could be generated for '{sheet_name}'.")
            continue
        cols = st.columns(2)
        for i, viz in enumerate(visualizations):
            with cols[i % 2]:
                with st.expander(f"**{viz['fig'].layout.title.text}**", expanded=False):
                    # --- YAHAN BADLAAV KIYA GAYA HAI ---
                    # Har chart ko ek unique key di gayi hai
                    st.plotly_chart(
                        viz['fig'],
                        use_container_width=True,
                        key=f"auto_chart_{sheet_name}_{i}" # Unique key
                    )
                    st.markdown(f"**Analysis**: {viz['analysis']}")