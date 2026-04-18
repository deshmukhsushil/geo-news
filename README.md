# Geo News 🌏 — Geopolitical News Tracker

A small data + app project that:
1) fetches news articles by **keyword** (via NewsAPI),
2) stores raw articles in **Snowflake**,
3) generates LLM summaries using **Cohere** and stores them back in Snowflake,
4) models curated tables with **dbt**, and
5) displays results in a **Streamlit** UI.

> Note: The current code is keyword-driven. “Geo/location-based personalization” is not implemented in the files shown.

---

## Tech Stack (as implemented)

- **UI**: Streamlit (`streamlit/app.py`, `project_root/app.py`)
- **Data warehouse**: Snowflake (via `snowflake-sqlalchemy` / SQLAlchemy)
- **Ingestion**: NewsAPI (`fetch_1.py`)
- **Summarization**: Cohere (`summarize_article.py`, `project_root/cohere_utils.py`)
- **Transformations / marts**: dbt + dbt-snowflake (`dbt_geotracker/`)
- **API (planned/optional)**: FastAPI + Uvicorn (present in `requirements.txt`; `project_root/app.py` calls `http://localhost:8000/summarize`)

---

## Repository Structure

- `streamlit/app.py`  
  Streamlit app that queries Snowflake for the latest articles for a keyword and (optionally) summarizes content with Cohere.

- `project_root/app.py`  
  Alternate Streamlit UI that calls a local API endpoint (`/summarize`) on `localhost:8000`.

- `fetch_1.py`  
  CLI script:
  - prompts for a keyword
  - fetches up to 50 results from NewsAPI
  - filters to max 5 articles per source
  - inserts into a Snowflake table `raw_articles`

- `summarize_article.py`  
  Batch job:
  - selects articles in `raw_articles` not yet present in `summarized_articles`
  - calls Cohere Summarize
  - inserts into `summarized_articles` with a `generated_at` timestamp

- `dbt_geotracker/`  
  dbt project that defines sources (`raw.raw_articles`, `raw.summarized_articles`) and builds a mart table joining raw + summaries.

---

## Data Model (Snowflake)

The dbt project expects these sources:

- `raw.raw_articles`
- `raw.summarized_articles`

The mart model `dbt_geotracker/models/marts/summarized_articles.sql` produces a table containing:

- `article_id`
- `title`
- `url`
- `published_at`
- `source_name`
- `keyword`
- `summary`
- `generated_at`

---

## Environment Variables

Create a `.env` file (project root) with at least:

- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- `SNOWFLAKE_WAREHOUSE`

- `NEWS_API_KEY` (for ingestion via NewsAPI)
- `COHERE_API_KEY` (for summarization)

> Security note: do **not** commit secrets (Snowflake passwords, API keys) to the repo.

---

## Setup

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

### 2) Configure `.env`

Add your Snowflake, NewsAPI, and Cohere credentials (see above).

---

## Usage

### A) Fetch raw articles into Snowflake

`fetch_1.py` will ask for a keyword in the terminal and then insert articles into `raw_articles`.

```bash
python fetch_1.py
```

### B) Generate summaries into `summarized_articles`

This job summarizes unsummarized rows and inserts into Snowflake.

```bash
python summarize_article.py
```

### C) Run dbt models (optional but recommended)

From within `dbt_geotracker/`, configure a dbt profile and run:

```bash
cd dbt_geotracker
dbt run
```

This will build the mart model (table) that joins raw articles and summaries.

> The repo includes `dbt_geotracker/profiles.yml`, but you should typically use your user-level dbt profiles location and never store real credentials in git.

### D) Run the Streamlit app

Option 1 (Snowflake query UI):
```bash
streamlit run streamlit/app.py
```

Option 2 (API-calling UI; requires an API server on localhost:8000):
```bash
streamlit run project_root/app.py
```

---

## Current Limitations / What’s *not* implemented (yet)

Based on the files shown:
- No actual geolocation detection or user-location personalization logic is present.
- The FastAPI server that serves `GET /summarize` is not included in the snippets provided (but dependencies suggest it’s intended).

---

## Credits

- News data: NewsAPI
- Summaries: Cohere
- Warehouse: Snowflake
- Modeling: dbt
- UI: Streamlit
