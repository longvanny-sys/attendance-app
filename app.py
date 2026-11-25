import pandas as pd
import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
month = st.selectbox("ជ្រើសរើសឈ្មោះ", ["ឡុង វណ្ណនី", "ឈន ធារ៉ា", "ហែម ណារ៉ា"])
try:
    df = pd.read_csv(csv_url)
    st.subheader("ទិន្នន័យទាំងអស់")
    st.dataframe(df)

    if "Name" in df.columns:
        names = df["Name"].dropna().unique().tolist()
        selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)

        filtered_df = df[df["Name"] == selected_name]
        st.subheader("លទ្ធផលតាមឈ្មោះ")
        st.dataframe(filtered_df)
    else:
        st.warning("រកមិនឃើញជួរឈរ 'Name' នៅក្នុង Sheet ទេ។")
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
import streamlit as st
option = st.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"),
)

st.write("You selected:", option)

