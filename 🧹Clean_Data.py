# pages/1_🧹_Clean_Data.py
import streamlit as st
from utils import clean_data
import pandas as pd

st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")
st.title("🧹 Automatic Data Cleaning")
st.markdown("Review and apply automated cleaning processes like removing duplicates and filling missing values.")

# Function to convert DataFrame to CSV for download
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

if 'dfs' not in st.session_state:
    st.info("Please upload a data file on the 'Home' page to use this feature.")
else:
    original_dfs = st.session_state['original_dfs']
    
    if st.button("✨ Clean My Data"):
        cleaned_dfs = {}
        with st.spinner("Cleaning in progress..."):
            for sheet_name, df in original_dfs.items():
                cleaned_df, actions = clean_data(df.copy())
                cleaned_dfs[sheet_name] = cleaned_df
                
                with st.container(border=True):
                    st.subheader(f"Sheet: '{sheet_name}'")
                    
                    if actions:
                        with st.expander("View Cleaning Log"):
                            for action in actions:
                                st.info(f"✔️ {action}")
                    else:
                        st.success("✔️ No cleaning was needed for this sheet.")

                    st.markdown("#### Cleaned Data Preview (Poori Sheet)")
                    
                    # BADLAAV #1: .head() ko hataya gaya taaki poori sheet dikhe
                    st.dataframe(cleaned_df)
                    
                    # BADLAAV #2: Cleaned data ko download karne ke liye button
                    csv_data = convert_df_to_csv(cleaned_df)
                    st.download_button(
                       label=f"📥 Download '{sheet_name}' as CSV",
                       data=csv_data,
                       file_name=f"cleaned_{sheet_name}.csv",
                       mime="text/csv",
                       key=f"download_{sheet_name}" # Unique key for each button
                    )

        # Update session state with all cleaned dataframes
        st.session_state['dfs'] = cleaned_dfs
        st.success("All sheets have been processed! The cleaned data will now be used in other pages.")