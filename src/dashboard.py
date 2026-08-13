import streamlit as st
import db_connect



def count_contract_type(conn):
    contract_type_count_query = 'SELECT contract_type, COUNT(*) FROM postings GROUP BY contract_type'
    result = conn.execute(contract_type_count_query).fetchall()
    contract_type_count = {row[0]:row[1] for row in result}
    return contract_type_count

def count_location(conn):
    location_count_query = 'SELECT location, COUNT (*) FROM postings GROUP BY location'
    result = conn.execute(location_count_query).fetchall()
    location_count = {row[0]:row[1] for row in result}
    return location_count

conn = db_connect.get_connection()
st.bar_chart(count_contract_type(conn))
st.bar_chart(count_location(conn))