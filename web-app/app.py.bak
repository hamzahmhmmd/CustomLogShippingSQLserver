import os
import datetime
import pyodbc
import pymongo
import pandas as pd
import altair as alt
import streamlit as st
from collections import Counter

st.title('Test')

client = pymongo.MongoClient(host="mongoc")

@st.cache(ttl=600)
def get_data():
    db = client.logshipping
    items = db.lsdb.find()
    items = list(items)  # make hashable for st.cache
    return items

_id, driver, server, port, ls_database, user, password, trusted_conn = get_data()[0].values()
conn_str = (f'Driver={driver};Server={server},{port};Database={ls_database};UID={user};PWD={password};Trusted_Connection={trusted_conn}')
pass_login = f''',{port} -U {user} -P {password} -d {ls_database} '''

# pyodbc
def read(conn_str, query):
    cnxn = pyodbc.connect(conn_str)
    return pd.read_sql_query(query, cnxn)

st.dataframe(read(conn_str, query="SELECT * FROM PMAG_Databases"))

os.system(f'''
/opt/mssql-tools/bin/sqlcmd -S {server}{pass_login}-Q "SELECT * FROM PMAG_Databases"
''')
