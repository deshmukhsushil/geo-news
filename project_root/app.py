import streamlit as st
import requests

st.title("Geopolitical News Tracker 🔍")
keyword = st.text_input("Enter keyword to search for articles")

if keyword:
    with st.spinner("Fetching summaries..."):
        try:
            res = requests.get(f"http://localhost:8000/summarize", params={"keyword": keyword})
            data = res.json()
            for item in data["results"]:
                st.subheader(item["title"])
                st.markdown("**Summary:**")
                st.write(item["summary"])
                st.markdown(f"[Read full article]({item['url']})", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
