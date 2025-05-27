import os
import streamlit as st
from serpapi import GoogleSearch
from newsdataapi import NewsDataApiClient
import requests
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

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
    return results.get("organic_results", [])

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
# Function: Generate PDF Report
# -----------------------------
def generate_pdf_report(company_name, google_results, newsdata_articles, gnews_articles):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{company_name.replace(' ', '_')}_{date_str}.pdf"
    filepath = Path("reports") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Vision Hacker Report on {company_name}", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    # Overview from Google Results
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="📌 Overview:", ln=True)
    pdf.set_font("Arial", '', 12)
    if google_results:
        snippet = google_results[0].get("snippet", "No overview found.")
        pdf.multi_cell(0, 10, snippet)
        pdf.ln(5)
    else:
        pdf.multi_cell(0, 10, "No search data available.")

    # News from NewsData
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="📰 Recent News from NewsData.io:", ln=True)
    pdf.set_font("Arial", '', 12)
    if newsdata_articles:
        for article in newsdata_articles[:3]:
            pdf.multi_cell(0, 10, f"- {article['title']} ({article['link']})")
            pdf.ln(2)
    else:
        pdf.cell(200, 10, txt="No news articles found.", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="📰 Recent News from GNews:", ln=True)
    pdf.set_font("Arial", '', 12)
    if gnews_articles:
        for article in gnews_articles[:3]:
            pdf.multi_cell(0, 10, f"- {article['title']} ({article['url']})")
            pdf.ln(2)
    else:
        pdf.cell(200, 10, txt="No news articles found.", ln=True)

    # Mock diagnosis
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="⚠️ Pain Points (Mock AI Diagnosis):", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt="- High public exposure may demand better PR handling.", ln=True)
    pdf.cell(200, 10, txt="- Competitor pressure in regional markets.", ln=True)

    # Suggestions
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="💡 Suggested Actions:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt="- Invest in localized branding and influencer partnerships.", ln=True)
    pdf.cell(200, 10, txt="- Boost digital engagement through targeted campaigns.", ln=True)

    pdf.output(str(filepath))
    return filepath

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
            report_path = generate_pdf_report(company, google_data, news_data, gnews_data)

            st.success(f"Report generated!")
            with open(report_path, "rb") as f:
                st.download_button("📄 Download PDF Report", f, file_name=report_path.name)
        except Exception as e:
            st.error(f"An error occurred: {e}")
