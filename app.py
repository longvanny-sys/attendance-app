import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?gid=1512199347#gid=1512199347" 
csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
try:
	import pandas as pd
	df = pd.read_csv(csv_url)
	st.dataframe(df)
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
