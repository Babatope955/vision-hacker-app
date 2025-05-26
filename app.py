import streamlit as st
from fpdf import FPDF
import base64

st.set_page_config(page_title="Vision Hacker", layout="centered")

st.title("🔍 Vision Hacker - IDEAL Model Tool")
query = st.text_input("Enter a name, brand or company to analyze")

# FAKE analysis - for demo; replace this with real logic later
def run_fake_analysis(query):
    return f"""
    • {query} has a strong online presence but lacks consistent messaging.
    • There’s untapped potential in connecting with younger audiences.
    • SEO performance is below industry average.
    • Content engagement could increase with more storytelling and brand consistency.
    """

def generate_pdf_report(query, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Vision Hacker Report: {query}", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, analysis)
    pdf_output = f"{query}_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

def generate_email_pitch(query, analysis):
    return f"""Subject: Opportunity to Strengthen {query}'s Brand

Hi {query},

I recently reviewed your digital presence and identified some improvement areas:

{analysis}

Would you be open to a short conversation about solutions? I’d love to share how I can help.

Best regards,  
[Your Name]  
Vision Hacker  
"""

if st.button("🚀 Analyze"):
    if not query:
        st.warning("Please enter a name or brand to analyze.")
    else:
        analysis = run_fake_analysis(query)
        st.subheader("🧠 Analysis Summary")
        st.write(analysis)

        # PDF
        pdf_file = generate_pdf_report(query, analysis)
        with open(pdf_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{pdf_file}">📄 Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Email
        st.subheader("✉️ Suggested Email Pitch")
        email = generate_email_pitch(query, analysis)
        st.code(email)
