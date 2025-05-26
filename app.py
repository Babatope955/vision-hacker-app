import streamlit as st
import openai
import requests
from serpapi import GoogleSearch

# PAGE CONFIG
st.set_page_config(page_title="Vision Hacker IDEAL Model", layout="centered")
st.title("🔍 Vision Hacker IDEAL Model")

# INPUTS
st.write("Enter a public figure, company or brand. This tool will analyze gaps and opportunities using the IDEAL model.")
query = st.text_input("Who or what do you want to analyze?")

openai_api = st.secrets["OPENAI_KEY"] if "OPENAI_KEY" in st.secrets else st.text_input("Enter your OpenAI API Key", type="password")
serpapi_key = st.secrets["SERPAPI_KEY"] if "SERPAPI_KEY" in st.secrets else st.text_input("Enter your SerpAPI Key", type="password")

# RUN ANALYSIS
if st.button("Run IDEAL Analysis") and query and openai_api and serpapi_key:
    st.info("Analyzing... Please wait ⏳")

    # STEP 1 — GET REAL-TIME DATA FROM SERPAPI
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_key,
        "num": 10
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])
    
    snippets = [item.get("snippet", "") for item in organic_results]
    combined_text = " ".join(snippets)

    # STEP 2 — RUN OPENAI ANALYSIS USING IDEAL FRAMEWORK
    prompt = f"""
    You are a Vision Hacker. Use the IDEAL model to analyze the following person or company based on this info:
    
    [DATA]: {combined_text}

    IDEAL stands for:
    I - Identify core mission and current position.
    D - Detect opportunity gaps and hidden weaknesses.
    E - Evaluate external perception and digital presence.
    A - Align new creative strategies to their values.
    L - Launch actionable steps or innovation suggestions.

    Give the analysis in a simple, smart way.
    """

    openai.api_key = openai_api
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert strategist and brand analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

    output = response["choices"][0]["message"]["content"]
    st.success("✅ IDEAL Analysis Complete")
    st.markdown(output)

    # OPTIONAL DOWNLOAD
    st.download_button("📄 Download Report", output, file_name=f"{query}_IDEAL_analysis.txt")

