import streamlit as st
import db_connect
import numpy as np



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

def bin_distance(conn):
    distance_query = 'SELECT entfernung FROM postings'
    result = conn.execute(distance_query).fetchall()
    distance_list = [row[0] for row in result]
    binning_result = np.histogram(distance_list, bins=[0,10,20,30,100])
    counts, edges = binning_result
    binning_distance_dict = {f'{edges[i]}-{edges[i+1]}': counts[i] for i in range(len(counts))}
    return binning_distance_dict

conn = db_connect.get_connection()
st.bar_chart(count_contract_type(conn))
st.bar_chart(count_location(conn))
st.bar_chart(bin_distance(conn))