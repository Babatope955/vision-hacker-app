import streamlit as st

st.set_page_config(page_title="Vision Hacker IDEAL Model")
st.title("Vision Hacker IDEAL Model")

st.write("Enter a company or person’s name to run an opportunity analysis:")

query = st.text_input("Who do you want to analyze?")

if st.button("Run IDEAL Analysis") and query:
    st.success(f"Analyzing {query}...")
    st.write("✅ Opportunity gaps and predictions will appear here in the next version.")
