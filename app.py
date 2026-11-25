import pandas as pd
import streamlit as st

st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/export?format=csv&gid=2089004"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
try:
    df = pd.read_csv(csv_url)
    st.subheader("ទិន្នន័យទាំងអស់")
    st.dataframe(df)

    if not df.empty:
        st.write("តម្លៃ Cell ដំបូង:", df.iloc[0, 0])

    if "Name" in df.columns:
        names = df["Name"].dropna().unique().tolist()
        selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)

        filtered_df = df[df["Name"] == selected_name]
        st.subheader("លទ្ធផលតាមឈ្មោះ")
        st.dataframe(filtered_df)

        if "Status" in df.columns and not filtered_df.empty:
            st.write("Status:", filtered_df["Status"].iloc[0])
    else:
        st.warning("រកមិនឃើញជួរឈរ 'Name' នៅក្នុង Sheet ទេ។")

except Exception as e:
    st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
