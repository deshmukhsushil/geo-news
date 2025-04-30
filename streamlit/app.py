import os
import streamlit as st
from sqlalchemy import create_engine, text  # Note: text import added
import snowflake.connector
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
from pathlib import Path  
import requests  

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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
    try:
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
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return []

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
