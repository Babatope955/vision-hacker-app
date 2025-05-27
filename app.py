import streamlit as st
import requests
import os

# Load API key from Streamlit Secrets
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

# Search function using SerpAPI
def search_with_serpapi(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "engine": "google",
        "api_key": SERPAPI_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# Analysis function
def analyze_results(results):
    if "organic_results" not in results:
        return "No results found or API error."

    insights = []

    titles = [res.get("title", "") for res in results["organic_results"]]
    snippets = [res.get("snippet", "") for res in results["organic_results"]]

    # Basic keyword checks
    if not any("vision" in s.lower() for s in snippets):
        insights.append("⚠️ No clear vision or mission found in public results.")
    if not any("contact" in s.lower() or "email" in s.lower() for s in snippets):
        insights.append("📭 No contact information is visible — may reduce trust.")
    if any("controversy" in s.lower() or "scandal" in s.lower() for s in snippets):
        insights.append("🚨 Potential reputation risks found.")

    if not insights:
        insights.append("✅ Everything looks generally clean and structured.")

    return "\n".join(insights)

# Streamlit app UI
st.title("🔎 Vision Hacker Lite")
query = st.text_input("Enter name of a company, influencer, or product to analyze:")

if st.button("Analyze"):
    with st.spinner("Searching..."):
        search_data = search_with_serpapi(query)
        st.subheader("🔍 Top Search Results")
        if "organic_results" in search_data:
            for i, res in enumerate(search_data["organic_results"][:5]):
                st.markdown(f"**{i+1}. {res.get('title', '')}**")
                st.write(res.get("snippet", ""))
                st.write(res.get("link", ""))
        else:
            st.error("No results found or SerpAPI quota exceeded.")

        st.subheader("🧠 Auto Insights")
        analysis = analyze_results(search_data)
        st.write(analysis)
