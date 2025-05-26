import streamlit as st
from serpapi import GoogleSearch
import openai
from fpdf import FPDF
import datetime

# Load API keys from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]

def serpapi_search(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": 5
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    snippets = []
    if "organic_results" in results:
        for result in results["organic_results"]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            combined = f"{title}\n{snippet}\n{link}"
            snippets.append(combined)
    return "\n\n".join(snippets)

def openai_analyze(text):
    system_prompt = (
        "You are a business analyst. Analyze the following information about a company or person. "
        "Identify pain points, gaps, opportunities, and suggest tailored solutions."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def create_pdf_report(title, analysis_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"IDEAL Model Analysis Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Subject: {title}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, analysis_text)
    filename = f"IDEAL_Report_{title.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def main():
    st.title("🚀 IDEAL Model Business Analyzer")
    st.write("Enter a company or person name to analyze their public data and get tailored solutions.")

    query = st.text_input("Enter company or person name:")

    if st.button("Analyze") and query:
        with st.spinner("Fetching data from Google..."):
            scraped_text = serpapi_search(query)
        
        if not scraped_text:
            st.warning("No data found. Try a different name or keyword.")
            return
        
        st.subheader("🔍 Raw Data Snippets from Google Search:")
        st.write(scraped_text)

        with st.spinner("Analyzing data with OpenAI GPT..."):
            analysis = openai_analyze(scraped_text)
        
        st.subheader("🧠 IDEAL Model Analysis:")
        st.write(analysis)

        if st.button("Generate PDF Report"):
            pdf_file = create_pdf_report(query, analysis)
            with open(pdf_file, "rb") as f:
                st.download_button(label="Download Report PDF", data=f, file_name=pdf_file, mime="application/pdf")

if __name__ == "__main__":
    main()
