import streamlit as st
import db_connect
import numpy as np

from extract_jobs_skills import SKILLS_DICTIONARY
from match import matching, get_posting_details

st.set_page_config(page_title="Find Your Work", layout="wide")


def count_contract_type(conn):
    contract_type_count_query = 'SELECT contract_type, COUNT(*) FROM postings GROUP BY contract_type'
    result = conn.execute(contract_type_count_query).fetchall()
    return {(row[0] or "Unknown"): row[1] for row in result}

def count_location(conn):
    location_count_query = 'SELECT location, COUNT (*) FROM postings GROUP BY location'
    result = conn.execute(location_count_query).fetchall()
    return {(row[0] or "Unknown"): row[1] for row in result}

def bin_distance(conn):
    distance_query = 'SELECT entfernung FROM postings'
    result = conn.execute(distance_query).fetchall()
    # entfernung can be NULL (e.g. remote postings with no fixed distance) -
    # np.histogram can't handle None, so drop those before binning.
    distance_list = [row[0] for row in result if row[0] is not None]
    if not distance_list:
        return {}
    binning_result = np.histogram(distance_list, bins=[0, 10, 20, 30, 100])
    counts, edges = binning_result
    return {f'{edges[i]}-{edges[i+1]}': counts[i] for i in range(len(counts))}

def rank_top10_companies(conn):
    company_offers_query = 'SELECT name, COUNT(*) FROM postings JOIN companies ON postings.company_id = companies.company_id\
                             GROUP BY name ORDER BY COUNT(name) DESC LIMIT 10'
    result = conn.execute(company_offers_query).fetchall()
    return {row[0]: row[1] for row in result}


st.title("Find Your Work")

tab_match, tab_market = st.tabs(["Match my CV", "Market overview"])

with tab_match:
    st.subheader("Paste your CV to find your best-matching postings")
    st.caption(
        "Ranks scraped postings against your CV by keyword-skill overlap (Jaccard similarity). "
        "This is a baseline - see the README roadmap for the planned embedding-based upgrade."
    )
    cv_text = st.text_area("CV text (paste as plain text)", height=250,
                            placeholder="Paste your CV / resume text here...")
    top_n = st.slider("How many matches to show", min_value=5, max_value=50, value=10)

    if st.button("Find matches", type="primary"):
        if not cv_text.strip():
            st.warning("Paste some CV text first.")
        else:
            ranked, cv_skills = matching(cv_text, SKILLS_DICTIONARY)
            if not ranked:
                st.info("No postings in the database yet - run the ingestion pipeline first.")
            else:
                st.write(f"Skills detected in your CV: {', '.join(sorted(cv_skills)) or '(none found)'}")
                shown = [r for r in ranked if r[1] > 0][:top_n] or ranked[:top_n]
                details = get_posting_details([pid for pid, _ in shown])
                for rank, (posting_id, score) in enumerate(shown, start=1):
                    info = details.get(posting_id, {})
                    with st.container(border=True):
                        st.markdown(f"**{rank}. {info.get('title', '(unknown title)')}** — {score:.0%} match")
                        st.write(f"{info.get('company', '?')} · {info.get('location', '?')} · {info.get('contract_type') or '?'}")
                        if info.get("german_level_requirement"):
                            st.write(f"German level required: {info['german_level_requirement']}")
                        if info.get("apply_url"):
                            st.markdown(f"[Open posting]({info['apply_url']})")

with tab_market:
    conn = db_connect.get_connection()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Contract type breakdown")
        st.bar_chart(count_contract_type(conn))
        st.subheader("Distance from search center (km)")
        dist = bin_distance(conn)
        if dist:
            st.bar_chart(dist)
        else:
            st.info("No distance data available.")
    with col2:
        st.subheader("Postings by location")
        st.bar_chart(count_location(conn))
        st.subheader("Top 10 companies by posting count")
        st.bar_chart(rank_top10_companies(conn))
    conn.close()
