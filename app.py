import pandas as pd
import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
name = st.selectbox("ជ្រើសរើសឈ្មោះ", ["ឡុង វណ្ណនី", "ឈន ធារ៉ា", "ហែម ណារ៉ា"])
try:
    df = pd.read_csv(csv_url)
	value = df.iloc[0, 0]
	value = df.iloc[2, 1]
cell_value = df.loc[0, "Name"]
st.write("តម្លៃក្នុង Cell:", cell_value)
    st.subheader("ទិន្នន័យទាំងអស់")
    st.dataframe(df)
if not df.empty:
	st.write("តម្លៃ Cell ដំបូង:", df.iloc[0, 0])
if "Name" in df.columns:
        names = df["Name"].dropna().unique().tolist()
        selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)
        filtered_df = df[df["Name"] == selected_name]
        st.subheader("លទ្ធផលតាមឈ្មោះ")
		name_value = df.loc[0, "Name"]
name_value = df.at[0, "Name"]
	result = df.loc[df["Name"] == "ឡុង វណ្ណនី", "Status"].values[0]
st.write("Status:", result)
        st.dataframe(filtered_df)
    else:
        st.warning("រកមិនឃើញជួរឈរ 'Name' នៅក្នុង Sheet ទេ។")
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
st.write("You selected:", option)
