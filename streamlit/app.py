import streamlit as st
import duckdb
import pandas as pd

def get_connection():
    return duckdb.connect("duckdb/database.db")

def load_data():
    conn = get_connection()
    df = conn.execute("SELECT * FROM clean_events").df()
    conn.close()
    return df

def main():
    st.set_page_config(page_title="Geopolitics Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("🌍 Geopolitical Events")

    df = load_data()

    search_query = st.text_input("🔎 Search for Country / Title")

    if search_query:
        df = df[
            df['sourcecountry'].str.contains(search_query, case=False, na=False) |
            df['title'].str.contains(search_query, case=False, na=False)
        ]

    st.dataframe(df, use_container_width=True)

    st.bar_chart(df['sourcecountry'].value_counts())

if __name__ == "__main__":
    main()
