import streamlit as st
from openai import OpenAI
import requests

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Vision Hacker: Company Analysis Tool")

# Input from user
company_name = st.text_input("Enter the name of the company you want to analyze")

# Main analysis
if st.button("Run Analysis") and company_name:
    with st.spinner("Analyzing..."):

        # You can expand this to include scraping and SERP API if needed
        prompt = f"""
        Use the IDEAL framework to analyze this company: {company_name}.

        Step 1: Identify - Who are they, what do they do?
        Step 2: Diagnose - What problems or blind spots might they have?
        Step 3: Evaluate - How urgent and big are these problems?
        Step 4: Act - What quick, high-impact solutions can help them?
        Step 5: Launch - Package these ideas in a pitch-worthy summary.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )

        result = response.choices[0].message.content
        st.subheader("📊 AI Report")
        st.write(result)

        # Optional: Download as PDF (simple text for now)
        st.download_button("Download as text", result, file_name=f"{company_name}_report.txt")

