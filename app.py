import streamlit as st
from serpapi import GoogleSearch

# Put your SerpApi key here or load from Streamlit secrets
SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY", "YOUR_SERPAPI_API_KEY")

st.title("Company Info Finder with SerpApi")

company_name = st.text_input("Enter company name")

if company_name:
    params = {
        "engine": "google",
        "q": company_name,
        "api_key": SERPAPI_API_KEY,
        "num": 5  # number of results
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "error" in results:
        st.error(f"SerpApi error: {results['error']}")
    else:
        organic_results = results.get("organic_results", [])
        if organic_results:
            st.subheader(f"Top {len(organic_results)} Google results for '{company_name}':")
            for idx, result in enumerate(organic_results, start=1):
                st.markdown(f"**{idx}. [{result.get('title', 'No title')}]({result.get('link', '#')})**")
                snippet = result.get("snippet")
                if snippet:
                    st.write(snippet)
                st.write("---")
        else:
            st.write("No organic results found.")
