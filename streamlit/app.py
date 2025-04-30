import streamlit as st
import requests

st.set_page_config(page_title="Geopolitical News Tracker", page_icon="🗞️")

st.title("🗺️ Geopolitical News Tracker")
st.markdown("Enter a keyword (e.g., `Russia`, `NATO`, `Iran`) to fetch and summarize news articles.")

# Input field for keyword
keyword = st.text_input("🔍 Keyword", placeholder="e.g., Ukraine, sanctions, oil")

# Button to trigger fetch and summarize
if st.button("Fetch Summaries") and keyword:
    with st.spinner(f"Fetching and summarizing news for: `{keyword}`"):
        try:
            # Adjust the URL if your FastAPI is hosted elsewhere
            response = requests.get("http://localhost:8000/summarize", params={"keyword": keyword})
            response.raise_for_status()
            data = response.json()

            if not data["results"]:
                st.warning("No articles found for that keyword.")
            else:
                st.success(f"Found {len(data['results'])} summarized articles.")
                for idx, item in enumerate(data["results"]):
                    with st.expander(f"📰 {item['title']}"):
                        st.markdown("**📝 Summary:**")
                        st.markdown(item["summary"])
                        st.markdown(f"🔗 [Read full article]({item['url']})", unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            st.error(f"🚨 API request failed: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

elif not keyword and st.button("Fetch Summaries"):
    st.warning("Please enter a keyword before submitting.")
