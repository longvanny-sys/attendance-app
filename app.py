import pandas as pd
import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
month = st.selectbox("ជ្រើសរើសខែ", ["ឡុង វណ្ណនី", "ឈន ធារ៉ា", "ហែម ណារ៉ា"])
try:
	df = pd.read_csv(csv_url)
	st.dataframe(df)
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
