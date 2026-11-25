import pandas as pd
import streamlit as st

st.title("តារាងបញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦ សាខា ប.ស.ស. ខេត្តពោធិ៍សាត់")

csv_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/export?format=csv&gid=2089000004"

try:
    # អានទិន្នន័យពី Google Sheet CSV
    df = pd.read_csv(csv_url, header=3)

    # ប្តូរឈ្មោះជួរឈរដែលជាប់ Unnamed ទៅជាឈ្មោះច្បាស់លាស់
    df = df.rename(columns={
        "Unnamed: 1": "ល.រ",
        "Unnamed: 2": "ឈ្មោះ",
        "Unnamed: 3": "ភេទ",
        "Unnamed: 4": "តួនាទី",
    })

    # កែឈ្មោះជួរឈរ Unnamed ដែលនៅសល់ (ប្រសិនបើមាន) ឱ្យក្លាយជា "ជួរឈរទទេ" ជំនួសការទុក "" ទទេ
    df.columns = [
        f"ជួរឈរ {i+1}" if (str(col).startswith("Unnamed:") or str(col).strip() == "") else str(col).strip()
        for i, col in enumerate(df.columns)
    ]

    # លុបជួរដេកដែលទទេទាំងស្រុង (ដូចជាជួរខណ្ឌដែលមានតែ None/NaN)
    df = df.dropna(how="all").reset_index(drop=True)

    # ស្វែងរកជួរឈរឈ្មោះបុគ្គលិក
    target_col = "ឈ្មោះ" if "ឈ្មោះ" in df.columns else ("Name" if "Name" in df.columns else None)

    # ==========================================
    # ផ្នែកទី ១៖ លទ្ធផលតាមឈ្មោះ (ដាក់នៅខាងលើ)
    # ==========================================
    st.subheader("លទ្ធផលតាមឈ្មោះ")

    if target_col:
        names = (
            df[target_col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )

        # យកចេញនូវជួរចំណងជើងផ្នែកដូចជា "I. ..." ឬ "IV. ..." ប្រសិនបើមិនមែនជាឈ្មោះមនុស្ស
        names = [n for n in names if not n.startswith(("I.", "II.", "III.", "IV.", "V."))]

        if names:
            selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)
            filtered_df = df[df[target_col].astype(str).str.strip() == selected_name]

            if "តួនាទី" in df.columns and not filtered_df.empty:
                st.write("តួនាទី:", filtered_df["តួនាទី"].iloc[0])
            elif "Status" in df.columns and not filtered_df.empty:
                st.write("Status:", filtered_df["Status"].iloc[0])

            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("មិនមានឈ្មោះបុគ្គលិកសម្រាប់បង្ហាញទេ។")
    else:
        st.warning("រកមិនឃើញជួរឈរ 'ឈ្មោះ' ឬ 'Name' នៅក្នុង Sheet ទេ។")

    st.divider()

    # ==========================================
    # ផ្នែកទី ២៖ ទិន្នន័យទាំងអស់ (ដាក់នៅខាងក្រោម)
    # ==========================================
    st.subheader("ទិន្នន័យទាំងអស់")
    st.write(f"ចំនួនជួរដេកសរុប (Total rows): {len(df)}")

    if not df.empty:
        st.write("តម្លៃ Cell ដំបូង:", df.iloc[0, 0])

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
