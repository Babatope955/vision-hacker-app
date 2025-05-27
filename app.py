import streamlit as st
import openai
import os
import requests

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]

# Streamlit UI
st.title("🧠 Business Intelligence Tool (IDEAL Framework)")

query = st.text_input("🔍 Enter a company or founder name to analyze:")

# Button to trigger the analysis
if st.button("Run Analysis") and query:
    with st.spinner("🔄 Gathering intelligence..."):

        # SERP API search
        serp_url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": "5"
        }
        serp_results = requests.get(serp_url, params=params).json()

        # Extract snippets
        snippets = []
        if "organic_results" in serp_results:
            for result in serp_results["organic_results"]:
                if "snippet" in result:
                    snippets.append(result["snippet"])

        # Format context
        combined_snippets = "\n".join(snippets[:5])

        # Phase 2–5: AI reasoning using OpenAI
        prompt = f"""
You are a startup analyst using the IDEAL framework:

Phase 1: Based on the info below, identify the company's purpose and current activities.
Phase 2: Diagnose its public perception, gaps, competitors, and pain points.
Phase 3: Evaluate urgency, opportunity size, and effort-to-impact ratio.
Phase 4: Act — suggest solutions like tech upgrades, brand shifts, hiring, culture tweaks.
Phase 5: Launch — create a compelling short pitch to send the company.

Company Name: {query}
Info:
{combined_snippets}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're an expert business analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )

        output = response["choices"][0]["message"]["content"]
        st.markdown("## 🔍 Analysis Output")
        st.markdown(output)
