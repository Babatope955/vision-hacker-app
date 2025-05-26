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
from fpdf import FPDF
import base64

def generate_pdf_report(query, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Vision Hacker Report: {query}", ln=True, align='C')
    
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Summary & Insights:\n")
    pdf.set_font("Arial", "I", 11)
    pdf.multi_cell(0, 10, analysis)

    # Save to a buffer
    pdf_output = f"{query}_vision_hacker_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

def generate_email_pitch(query, analysis):
    return f"""
Subject: Opportunity to Strengthen {query}'s Vision and Digital Impact

Hi {query},

I recently reviewed your online presence and found areas where your brand could grow stronger, clearer, and more compelling. Based on this quick scan, here are a few highlights:

{analysis}

I'd love to offer tailored recommendations or help you implement these improvements if you're open to it.

Looking forward to your response.

Warm regards,  
[Your Name]  
Vision Hacker — I Help People & Brands See What's Missing
"""

# UI for PDF and email
if query and analysis:
    if st.button("📄 Generate PDF Report"):
        pdf_file = generate_pdf_report(query, analysis)
        with open(pdf_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{pdf_file}">Click here to download the PDF report</a>'
            st.markdown(href, unsafe_allow_html=True)

    if st.button("✉️ Generate Email Pitch"):
        email = generate_email_pitch(query, analysis)
        st.subheader("📬 Suggested Pitch Email")
        st.code(email)
