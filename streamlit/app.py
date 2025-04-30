import os
import streamlit as st
from sqlalchemy import create_engine
import snowflake.connector
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get Snowflake connection
def get_snowflake_connection():
    # Get connection parameters from .env file
    connection_parameters = {
        "user": os.environ.get("SNOWFLAKE_USER"),
        "password": os.environ.get("SNOWFLAKE_PASSWORD"),
        "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
        "database": os.environ.get("SNOWFLAKE_DATABASE"),
        "schema": os.environ.get("SNOWFLAKE_SCHEMA"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE"),
        "role": os.environ.get("SNOWFLAKE_ROLE"),  # Optional
    }
    
    # Create URL for SQLAlchemy
    snowflake_url = URL(
        account=connection_parameters["account"],
        user=connection_parameters["user"],
        password=connection_parameters["password"],
        database=connection_parameters["database"],
        schema=connection_parameters["schema"],
        warehouse=connection_parameters["warehouse"],
        role=connection_parameters["role"]
    )
    
    # Create engine
    engine = create_engine(snowflake_url)
    return engine


# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Snowflake credentials
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

# Cohere API key
cohere_api_key = os.getenv("COHERE_API_KEY")

# Create Snowflake engine
def create_snowflake_engine():
    return create_engine(
        f'snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}'
    )

# Query Snowflake for latest articles for a keyword
def get_articles_from_snowflake(keyword):
    engine = create_snowflake_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT TITLE, DESCRIPTION, URL, CONTENT
            FROM raw_articles
            WHERE KEYWORD = :keyword
            ORDER BY PUBLISHED_AT DESC
            LIMIT 10
        """), {"keyword": keyword})
        return result.fetchall()

# Call Cohere to summarize the article
def summarize_article_with_cohere(text_input):
    headers = {
        "Authorization": f"Bearer {cohere_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command-r-plus",
        "prompt": f"Summarize this article in 3 bullet points:\n\n{text_input}",
        "temperature": 0.3,
        "max_tokens": 300
    }
    response = requests.post("https://api.cohere.ai/v1/generate", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['generations'][0]['text']
    else:
        return "Error in summarization"

# Streamlit UI
st.title("Geopolitical News Summary App")
st.markdown("Get summarized geopolitical news from multiple sources.")

# Input box
keyword = st.text_input("Enter a geopolitical keyword (e.g., NATO, China, Israel, Russia)", key="keyword_input")

# Fetch summaries
if st.button("Fetch Summaries", key="fetch_button") and keyword:
    st.info(f"Searching articles for keyword: `{keyword}`...")
    articles = get_articles_from_snowflake(keyword)

    if not articles:
        st.warning("No articles found for this keyword. Try a different one or run the backend fetcher.")
    else:
        st.success(f"Found {len(articles)} articles! Summarizing...")

        for i, article in enumerate(articles):
            st.subheader(f"{i+1}. {article.TITLE}")
            st.write(article.DESCRIPTION)
            st.markdown(f"[Read full article]({article.URL})")

            with st.spinner("Summarizing..."):
                summary = summarize_article_with_cohere(article.CONTENT or article.DESCRIPTION or article.TITLE)
                st.markdown("**Summary:**")
                st.markdown(summary.strip())

            st.markdown("---")

# Optional: Clear results
if st.button("Clear Results", key="clear_button"):
    st.experimental_rerun()
