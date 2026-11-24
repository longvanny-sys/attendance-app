import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQITfz4x1jmCOH3208JmRmQj92ZkfbIYjiU48wFfsVf4P__3RDZynz-KimXM530RvsYqfJ3TzUnhLz/pubhtml?gid=2089000004&single=true" 
csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
try:
	import pandas as pd
	df = pd.read_csv(csv_url)
	st.dataframe(df)
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
