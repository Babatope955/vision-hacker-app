import streamlit as st
from openai import OpenAI
import requests
from serpapi import GoogleSearch

# Set up API keys
OPENAI_KEY = st.secrets["OPENAI_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

client = OpenAI(api_key=OPENAI_KEY)

# Streamlit UI
st.set_page_config(page_title="Vision Hacker", layout="centered")
st.title("🔍 Vision Hacker IDEAL Model")
st.write("Enter a company, influencer, or individual you'd like to analyze.")

query = st.text_input("Who/What would you like to analyze?")

if st.button("Analyze"):
    if not query:
        st.warning("Please enter a valid name or company.")
    else:
        with st.spinner("Running analysis..."):

            # STEP 1: Get Google search summary
            params = {
                "q": query,
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "num": 5
            }
            search = GoogleSearch(params)
            results = search.get_dict()

            organic_results = results.get("organic_results", [])
            summary = "\n\n".join([res.get("snippet", "") for res in organic_results])

            # STEP 2: Ask OpenAI for analysis and solutions
            prompt = f"""
You are a visionary business analyst. Here's a summary about {query}:

{summary}

Based on this, identify:
1. Current strengths
2. Hidden or ignored weaknesses
3. Areas of opportunity
4. One disruptive solution to transform their results
5. A possible role I can create to provide this value

Use simple language. Keep it actionable.
"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic visionary and solution hacker."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )

            result = response.choices[0].message.content

            # Display result
            st.subheader("📊 Vision Hacker Analysis")
            st.markdown(result)
