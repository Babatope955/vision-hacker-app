import os
import streamlit as st
from serpapi import GoogleSearch
from newsdataapi import NewsDataApiClient
import requests
import json
from datetime import datetime
from pathlib import Path

# -----------------------------
# Set up Streamlit secrets
# -----------------------------
SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]
NEWSDATA_API_KEY = st.secrets["NEWSDATA_API_KEY"]
GNEWS_API_KEY = st.secrets["GNEWS_API_KEY"]
PHANTOMBUSTER_API_KEY = st.secrets["PHANTOMBUSTER_API_KEY"]

# -----------------------------
# Function: Search company info using SerpAPI
# -----------------------------
def search_google(company_name):
    params = {
        "engine": "google",
        "q": company_name,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

# -----------------------------
# Function: Get news using NewsData.io
# -----------------------------
def get_news_newsdata(company_name):
    api = NewsDataApiClient(apikey=NEWSDATA_API_KEY)
    response = api.news_api(q=company_name, language="en")
    return response['results']

# -----------------------------
# Function: Get news using GNews API
# -----------------------------
def get_news_gnews(company_name):
    url = f"https://gnews.io/api/v4/search?q={company_name}&token={GNEWS_API_KEY}&lang=en"
    response = requests.get(url)
    return response.json().get("articles", [])

# -----------------------------
# Function: Use PhantomBuster for social scraping
# -----------------------------
def get_phantom_data(company_name):
    # You will need to set up a PhantomBuster Phantom and use its API endpoint
    headers = {
        "X-Phantombuster-Key-1": PHANTOMBUSTER_API_KEY,
        "Content-Type": "application/json"
    }
    # Replace 'YOUR_AGENT_ID' with your actual Phantom ID
    url = f"https://api.phantombuster.com/api/v2/agent/YOUR_AGENT_ID/launch"
    data = {"arguments": {"search": company_name}}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# -----------------------------
# Function: Generate Report
# -----------------------------
def generate_report(company_name, search_results, news1, news2):
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = Path("reports") / f"{company_name.replace(' ', '_')}_{date_str}.txt"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"--- Report on {company_name} ---\n\n")
        f.write("--- Google Search Results ---\n")
        json.dump(search_results, f, indent=2)

        f.write("\n--- News from NewsData ---\n")
        for article in news1:
            f.write(f"{article['title']} - {article['link']}\n")

        f.write("\n--- News from GNews ---\n")
        for article in news2:
            f.write(f"{article['title']} - {article['url']}\n")

    return report_path

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🔍 Vision Hacker: Company Intelligence Tool")
company = st.text_input("Enter a company name to analyze:")

if st.button("Run Analysis") and company:
    with st.spinner("Running analysis..."):
        try:
            google_data = search_google(company)
            news_data = get_news_newsdata(company)
            gnews_data = get_news_gnews(company)
            # phantom_data = get_phantom_data(company)  # Optional if you've set up a Phantom

            report = generate_report(company, google_data, news_data, gnews_data)
            st.success(f"Report generated: {report.name}")
            with open(report, "r", encoding="utf-8") as file:
                st.download_button("Download Report", file, file_name=report.name)
        except Exception as e:
            st.error(f"An error occurred: {e}")
