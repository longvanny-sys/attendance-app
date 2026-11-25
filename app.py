import pandas as pd
import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
month = st.selectbox("ជ្រើសរើសឈ្មោះ", ["ឡុង វណ្ណនី", "ឈន ធារ៉ា", "ហែម ណារ៉ា"])
selected_name = st.selectbox(...)
filtered_df = df[df['Name']== selected_name]
	st.write(filtered.df)
try:
	df = pd.read_csv(csv_url)
	st.dataframe(df)
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
import streamlit as st
option = st.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"),
)

st.write("You selected:", option)

