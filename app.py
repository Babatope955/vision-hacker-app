import streamlit as st
import openai
import requests
from fpdf import FPDF
import datetime

# --- CONFIG --- #
openai.api_key = st.secrets["OPENAI_API_KEY"]  # set your key in Streamlit secrets or replace directly here
SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]

# --- FUNCTIONS --- #

def serpapi_search(query, num=5):
    """Search Google via SerpAPI and get snippets & links."""
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num,
        "hl": "en",
        "gl": "us",
    }
    res = requests.get(url, params=params).json()
    results = []
    if "organic_results" in res:
        for r in res["organic_results"][:num]:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            results.append(f"{title}\n{snippet}\n{link}\n")
    return "\n---\n".join(results)

def generate_analysis(text, query):
    prompt = f"""
You are an expert business analyst. Given the following information about {query}:

{text}

Please provide the analysis in the following structure:
1. Identify: Summarize who/what this company/person is and what they do.
2. Diagnose: What are their strengths, weaknesses, opportunities, and threats based on public info?
3. Evaluate: How urgent or big are the opportunities or problems?
4. Act: Suggest 3 actionable solutions or strategies to improve or capitalize on opportunities.
5. Pitch: Draft a short personalized email pitch offering consulting services to help.

Format the output clearly.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role":"system","content":"You are a helpful business analyst."},
            {"role":"user","content":prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content

def create_pdf(report_text, query):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Business Analysis Report: {query}", ln=True, align="C")
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(10)
    for line in report_text.split('\n'):
        pdf.multi_cell(0, 8, line)
    pdf_file = f"{query.replace(' ', '_')}_analysis_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

# --- STREAMLIT APP --- #

st.title("Vision Hacker — Business AI Analyst")

query = st.text_input("Enter a company or person name (or website):")

if st.button("Analyze"):
    if not query.strip():
        st.error("Please enter a valid company or person name.")
    else:
        with st.spinner("Fetching public info from Google..."):
            search_results = serpapi_search(query)
        st.subheader("Raw Search Results")
        st.text_area("", search_results, height=300)

        with st.spinner("Generating AI analysis and pitch..."):
            analysis = generate_analysis(search_results, query)
        st.subheader("AI Analysis & Recommendations")
        st.write(analysis)

        pdf_file = create_pdf(analysis, query)
        with open(pdf_file, "rb") as f:
            st.download_button(label="Download PDF Report", data=f, file_name=pdf_file, mime="application/pdf")

