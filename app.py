import streamlit as st
from openai import OpenAI
from serpapi import GoogleSearch
import os

# Load keys from environment or Streamlit secrets
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY") or os.getenv("SERPAPI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

st.title("🔍 Vision Hacker: The IDEAL Model Tool")
company_name = st.text_input("Enter a Company Name (e.g., Flutterwave Nigeria)")

if st.button("Analyze"):
    if not company_name:
        st.warning("Please enter a company name.")
    else:
        with st.spinner("Gathering insights..."):
            # SERPAPI SEARCH
            params = {
                "engine": "google",
                "q": company_name,
                "api_key": SERPAPI_API_KEY,
                "num": 5
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            snippets = [res.get("snippet", "") for res in organic_results[:5]]
            combined_snippets = "\n\n".join(snippets)

            prompt = f"""
            You are a business analyst using the IDEAL Model.

            Company: {company_name}

            Phase 1: IDENTIFY
            Based on this public content:
            {combined_snippets}

            1. What does this company do?
            2. What is its current brand perception?
            3. Who are its competitors?
            4. What challenges or gaps do you see?
            5. How urgent or strategic are those gaps?

            Then continue with:

            Phase 2: DIAGNOSE
            • Highlight branding, tech, product, hiring, or leadership issues.
            • Summarize public sentiment from the tone of these results.

            Phase 3: EVALUATE
            • Rate the urgency of their problem.
            • Suggest 1-2 low-effort, high-impact opportunities to help.

            Phase 4: ACT
            • Suggest solution ideas, new directions, or fixes.

            Phase 5: LAUNCH
            • Draft a short pitch email offering a solution.

            End with: “Final Output: PDF-ready summary for internal use”
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500
                )
            except Exception as e:
                st.error(f"OpenAI API error: {e}")
                st.stop()

            result_text = response.choices[0].message.content
            st.subheader("🧠 IDEAL Model Insights")
            st.write(result_text)

            # Optional: download button
            st.download_button("Download report as TXT", result_text, file_name="IDEAL_Report.txt")
