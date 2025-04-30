import requests
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict

# Absolute path to the .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get environment variables
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

def fetch_articles_from_newsapi(keyword):
    api_key = os.getenv('NEWS_API_KEY')
    print(f"Using API key: {api_key}")
    
    # Increase pageSize to 50 as requested
    response = requests.get(f"https://newsapi.org/v2/everything?q={keyword}&language=en&pageSize=50&apiKey={api_key}")
    
    # Check if the response is valid
    response.raise_for_status()
    
    # Get all articles
    all_articles = response.json().get('articles', [])
    
    # Limit to 5 articles per source
    sources_count = defaultdict(int)
    filtered_articles = []
    
    for article in all_articles:
        source_name = article['source']['name']
        if sources_count[source_name] < 5:  # Limit to 5 articles per source
            filtered_articles.append(article)
            sources_count[source_name] += 1
    
    print(f"Fetched {len(all_articles)} articles, filtered to {len(filtered_articles)} articles (max 5 per source)")
    return filtered_articles

# Function to insert articles into Snowflake
def insert_articles_into_snowflake(articles, keyword, engine):
    with engine.begin() as conn:
        for article in articles:
            # Use text-based SQL with named parameters instead of positional parameters
            conn.execute("""
                INSERT INTO raw_articles (id, title, url, published_at, source_name, content, summary, recommendations, keyword)
                VALUES (%(id)s, %(title)s, %(url)s, %(published_at)s, %(source_name)s, %(content)s, %(summary)s, %(recommendations)s, %(keyword)s)
            """, {
                'id': article['url'],  # Using URL as the unique ID
                'title': article['title'],
                'url': article['url'],
                'published_at': article['publishedAt'],
                'source_name': article['source']['name'],  # Changed column name from 'source' to 'source_name'
                'content': article['content'],
                'summary': article.get('summary', 'No summary available'),
                'recommendations': article.get('recommendations', '[]'),
                'keyword': keyword
            })

# Function to create the Snowflake engine
def create_snowflake_engine():
    return create_engine(
        f'snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}'
    )

# Main function that asks for user input in the terminal
def main():
    # Ask for keyword in the terminal
    keyword = input("Enter a keyword to search for articles: ")
    
    # Fetch articles from NewsAPI based on the entered keyword
    articles = fetch_articles_from_newsapi(keyword)
    
    if articles:
        # Create the Snowflake connection engine
        engine = create_snowflake_engine()
        
        # Insert the articles into Snowflake
        insert_articles_into_snowflake(articles, keyword, engine)
        
        # Confirm that articles have been inserted
        print(f"Successfully inserted {len(articles)} articles into Snowflake!")
    else:
        print(f"No articles found for the keyword '{keyword}'.")

if __name__ == "__main__":
    main()