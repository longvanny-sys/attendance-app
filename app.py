import pandas as pd
import streamlit as st

st.title("តារាងបញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦ សាខា ប.ស.ស. ខេត្តពោធិ៍សាត់")

csv_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/export?format=csv&gid=2089000004"

try:
    df = pd.read_csv(csv_url, header=3)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed: 0$")]
    df = df.rename(
        columns={
            "Unnamed: 1": "",
            "Unnamed: 2": "Name",
            "Unnamed: 3": "Gender",
            "Unnamed: 4": "Position",
            "Unnamed: 5": "ច្បាប់ប្រចាំឆ្នាំ(P)",
            "Unnamed: 6": "",
            "Unnamed: 7": "ច្បច្បាប់រយះពេលខ្លី(S)",
            "Unnamed: 8": "",
            "Unnamed: 9": "ច្បាប់ឈឺ(SL)",
            "Unnamed: 10": "",
        }
    )
    
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
