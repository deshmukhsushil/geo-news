import os
import cohere
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
import datetime

# Load env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Cohere API setup
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Snowflake setup
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

engine = create_engine(
    f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}"
)

def summarize_text(text):
    response = co.summarize(
        text=text,
        length="medium",
        format="bullets",
        model="summarize-xlarge",
    )
    return response.summary

def fetch_unsummarized_articles():
    query = """
    SELECT ID, TITLE, CONTENT
    FROM raw_articles
    WHERE ID NOT IN (SELECT RAW_ARTICLE_ID FROM summarized_articles)
    AND CONTENT IS NOT NULL
    LIMIT 20;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()

def insert_summaries(rows):
    insert_sql = """
    INSERT INTO summarized_articles (
        RAW_ARTICLE_ID, SUMMARY, GENERATED_AT
    ) VALUES (:id, :summary, :generated_at)
    """
    now = datetime.datetime.utcnow().isoformat()

    with engine.begin() as conn:
        for row in rows:
            article_id, title, content = row
            try:
                summary = summarize_text(content)
                conn.execute(text(insert_sql), {
                    "id": article_id,
                    "summary": summary,
                    "generated_at": now
                })
                print(f"✅ Summarized: {title}")
            except Exception as e:
                print(f"⚠️ Skipping {title} due to: {str(e)}")

def main():
    rows = fetch_unsummarized_articles()
    if not rows:
        print("No new articles to summarize.")
        return
    insert_summaries(rows)

if __name__ == "__main__":
    main()
