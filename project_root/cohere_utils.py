import cohere
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

cohere_api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

def summarize_text(text: str) -> str:
    try:
        response = co.summarize(text=text, model="command", length="medium", format="bullets")
        return response.summary
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Summary unavailable due to error."
