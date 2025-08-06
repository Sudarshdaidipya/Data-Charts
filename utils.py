# utils.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json
from io import StringIO
from langdetect import detect

# API client libraries
from groq import Groq
import google.generativeai as genai
from openai import OpenAI
import plotly.express as px

#  UNIFIED API CLIENT HANDLER 
def get_client(provider, api_key):
    if not api_key: return None, "API Key is missing."
    try:
        if provider == "Groq": return Groq(api_key=api_key), None
        elif provider == "Google Gemini":
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-1.5-pro-latest'), None
        elif provider == "OpenAI": return OpenAI(api_key=api_key), None
    except Exception as e: return None, f"Failed to initialize client: {e}"

#  UNIFIED RESPONSE GENERATOR 
def generate_response(client, provider, prompt):
    model_map = { "Groq": "llama3-70b-8192", "OpenAI": "gpt-4o" }
    try:
        if provider == "Google Gemini":
            response = client.generate_content(prompt)
            return response.text, None
        else:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model=model_map[provider],
            )
            return chat_completion.choices[0].message.content, None
    except Exception as e: return None, f"An error occurred while generating response: {e}"

# --- DATA CLEANING ---
def clean_data(df):
    actions = []
    initial_rows = len(df)
    df = df.drop_duplicates()
    rows_dropped = initial_rows - len(df)
    if rows_dropped > 0: actions.append(f"Removed {rows_dropped} duplicate rows.")
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_value = df[col].median()
                df[col].fillna(fill_value, inplace=True)
                actions.append(f"Filled missing numeric '{col}' with median ({fill_value:.2f}).")
            else:
                fill_value = df[col].mode()[0]
                df[col].fillna(fill_value, inplace=True)
                actions.append(f"Filled missing categorical '{col}' with mode ('{fill_value}').")
    return df, actions

# --- TASK-SPECIFIC FUNCTIONS ---
def generate_story(_dfs, client, provider):
    sheet_previews = "\n\n".join([f"--- Sheet Name: {name} ---\n{df.head().to_string()}" for name, df in _dfs.items()])
    prompt = f"You are a data storyteller. Analyze the provided data sheets to identify key trends and insights. Write a concise and engaging data story summarizing your findings.\n\nData Sheets:\n{sheet_previews}"
    response, error = generate_response(client, provider, prompt)
    return response if not error else f"Error: {error}"

def generate_prediction(_dfs, question, client, provider):
    sheet_previews = "\n\n".join([f"--- Sheet Name: {name} ---\n{df.head().to_string()}" for name, df in _dfs.items()])
    prompt = f"You are a strategic business forecaster. Based on the historical data provided, answer the user's question about the future. Analyze trends, make a clear prediction, and list key assumptions.\n\nUser's Question: '{question}'\n\nAvailable Data:\n{sheet_previews}"
    response, error = generate_response(client, provider, prompt)
    return response if not error else f"Error: {error}"

def generate_chart_code(_dfs, question, client, provider):
    sheet_previews = "\n\n".join([f"--- Sheet Name: {name} ---\n{df.head().to_string()}" for name, df in _dfs.items()])
    prompt = f"""
    You are a Python data visualization expert. Write ONLY Python code to create a chart based on the user's request.
    Your response MUST be a Python code block enclosed in ```python ... ```.
    **CRITICAL Instructions:**
    1.  **Only use columns that are visible in the Data Previews below.** Do NOT invent or assume column names.
    2.  When converting a column to datetime using `pd.to_datetime`, you MUST use the `errors='coerce'` argument.
    3.  The data is in a dictionary of DataFrames: `dfs['SheetName']`.
    4.  Use `matplotlib` or `seaborn`.
    5.  The code MUST create a list named `figs` and append the chart figure to it.
    6.  Do not use `plt.show()`.
    User Request: "{question}"
    Data Previews:
    {sheet_previews}
    """
    code, error = generate_response(client, provider, prompt)
    if error: return None, error
    if "```python" in code:
        match = re.search(r"```python\n(.*)```", code, re.DOTALL)
        if match: return match.group(1), None
    return code, None

def analyze_data(dfs):
    insights = {}
    for sheet_name, df in dfs.items():
        insights[sheet_name] = {'visualizations': []}
        for col in df.select_dtypes(include=np.number):
            insights[sheet_name]['visualizations'].append({'fig': px.histogram(df, x=col, title=f"Distribution of {col}"), 'analysis': f"Distribution for '{col}'."})
        for col in df.select_dtypes(include=['object', 'category']):
            value_counts = df[col].value_counts()
            if not value_counts.empty:
                if len(value_counts) > 10:
                    insights[sheet_name]['visualizations'].append({'fig': px.bar(value_counts.nlargest(10), title=f"Top 10 in {col}"), 'analysis': "Top 10 frequent categories."})
                    insights[sheet_name]['visualizations'].append({'fig': px.bar(value_counts.nsmallest(10), title=f"Least 10 in {col}"), 'analysis': "Least 10 frequent categories."})
                else:
                    insights[sheet_name]['visualizations'].append({'fig': px.bar(value_counts, title=f"Counts for {col}"), 'analysis': "Category counts."})
    return insights

def execute_code(code_string, dfs):
    try:
        local_vars = {'dfs': dfs, 'pd': pd, 'plt': plt, 'sns': sns, 'np': np, 'st': st}
        exec("import matplotlib.pyplot as plt\nfigs=[]", {}, local_vars)
        exec(code_string, {}, local_vars)
        figs = local_vars.get('figs', [])
        return figs, None
    except Exception as e: return None, f"Error executing code: {e}"

# --- NEW: Function to answer questions about the data story ---
def answer_story_question(data_story, question, _dfs, client, provider):
    sheet_previews = "\n\n".join([f"--- Sheet Name: {name} ---\n{df.head().to_string()}" for name, df in _dfs.items()])
    prompt = f"""
    You are a data analyst assistant. An initial data story has been generated from a dataset. The user has a follow-up question.
    
    **Original Data Story:**
    ---
    {data_story}
    ---
    
    **User's Follow-up Question:**
    ---
    {question}
    ---
    
    Based on the original story and the data previews below, please provide a concise answer to the user's question.
    
    **Data Previews:**
    {sheet_previews}
    """
    response, error = generate_response(client, provider, prompt)
    return response if not error else f"Error: {error}"