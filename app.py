import os
import streamlit as st
from serpapi import GoogleSearch
from newsdataapi import NewsDataApiClient
import requests
from datetime import datetime
from pathlib import Path
from fpdf import FPDF
from openai import OpenAI
import unicodedata

# -----------------------------
# Set up Streamlit secrets
# -----------------------------
SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]
NEWSDATA_API_KEY = st.secrets["NEWSDATA_API_KEY"]
GNEWS_API_KEY = st.secrets["GNEWS_API_KEY"]
PHANTOMBUSTER_API_KEY = st.secrets["PHANTOMBUSTER_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# Utility function to clean up non-latin characters
# -----------------------------
def sanitize_text(text):
    if not text:
        return ""
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

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
# Function: Get tweets using SerpApi Twitter engine
# -----------------------------
def get_tweets(company_name):
    params = {
        "engine": "twitter",
        "q": company_name,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    tweets = results.get("tweets", [])
    tweet_texts = [tweet.get("text", "") for tweet in tweets[:5]]
    return tweet_texts

# -----------------------------
# Function: Analyze tweets with OpenAI
# -----------------------------
def analyze_sentiment_with_openai(company_name, tweets):
    if not tweets:
        return "No tweet data available for sentiment analysis."
    prompt = f"""
    Analyze the public sentiment about {company_name} based on the following tweets:

    {'\n'.join(tweets)}

    Summarize the general tone, any common praises or complaints, and how the public perceives this company.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

# -----------------------------
# Function: Summarize Google results with OpenAI
# -----------------------------
def summarize_overview_with_openai(company_name, google_results):
    snippets = [res.get("snippet", "") for res in google_results[:5]]
    combined = "\n".join(snippets)
    prompt = f"""
    Based on the following search result snippets, provide a concise but insightful overview of what {company_name} does, their core services, public identity, and any standout observations:

    {combined}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# -----------------------------
# Function: Generate PDF Report
# -----------------------------
def generate_pdf_report(company_name, overview, newsdata_articles, gnews_articles, sentiment):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{company_name.replace(' ', '_')}_{date_str}.pdf"
    filepath = Path("reports") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=sanitize_text(f"Vision Hacker Report on {company_name}"), ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    # Overview from OpenAI summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=sanitize_text("Overview:"), ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, sanitize_text(overview or "No meaningful overview available."))

    # News from NewsData
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=sanitize_text("Recent News from NewsData.io:"), ln=True)
    pdf.set_font("Arial", '', 12)
    if newsdata_articles:
        for article in newsdata_articles[:3]:
            pdf.multi_cell(0, 10, sanitize_text(f"- {article['title']} ({article['link']})"))
            pdf.ln(2)
    else:
        pdf.cell(200, 10, txt=sanitize_text("No news articles found."), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=sanitize_text("Recent News from GNews:"), ln=True)
    pdf.set_font("Arial", '', 12)
    if gnews_articles:
        for article in gnews_articles[:3]:
            pdf.multi_cell(0, 10, sanitize_text(f"- {article['title']} ({article['url']})"))
            pdf.ln(2)
    else:
        pdf.cell(200, 10, txt=sanitize_text("No news articles found."), ln=True)

    # Sentiment Analysis
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=sanitize_text("Social Media Sentiment:"), ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, sanitize_text(sentiment))

    pdf.output(str(filepath))
    return filepath

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Vision Hacker: Company Intelligence Tool")
company = st.text_input("Enter a company name to analyze:")

if st.button("Run Analysis") and company:
    with st.spinner("Running analysis..."):
        try:
            google_data = search_google(company)
            news_data = get_news_newsdata(company)
            gnews_data = get_news_gnews(company)
            tweets = get_tweets(company)
            sentiment = analyze_sentiment_with_openai(company, tweets)
            overview = summarize_overview_with_openai(company, google_data)
            report_path = generate_pdf_report(company, overview, news_data, gnews_data, sentiment)

            st.success("Report generated!")
            with open(report_path, "rb") as f:
                st.download_button("Download PDF Report", f, file_name=report_path.name)
        except Exception as e:
            st.error(f"An error occurred: {e}")
