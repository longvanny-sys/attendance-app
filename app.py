import pandas as pd
import streamlit as st

st.set_page_config(page_title="បញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦", layout="wide")

st.title("តារាងបញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦ សាខា ប.ស.ស. ខេត្តពោធិ៍សាត់")

csv_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/export?format=csv&gid=2089000004"


def render_sheet_like_table(raw_df: pd.DataFrame, max_height: str = "460px"):
    """បង្ហាញតារាងជាទម្រង់ស្រដៀង Google Sheet (មាន Header 2 ជួរ និង Grid ព្រំដែនច្បាស់)"""
    # យក Header 2 ជួរ (ជួរ index 2 ជាក្រុមធំ, ជួរ index 3 ជាឈ្មោះកូន)
    top_row = raw_df.iloc[2].fillna("").astype(str).str.strip().tolist() if len(raw_df) > 2 else []
    sub_row = raw_df.iloc[3].fillna("").astype(str).str.strip().tolist() if len(raw_df) > 3 else []

    # ជួរទិន្នន័យចាប់ពីជួរ index 4 ចុះក្រោម (លុបជួរទទេទាំងស្រុងចេញ)
    body_df = raw_df.iloc[4:].dropna(how="all").reset_index(drop=True)
    num_cols = body_df.shape[1]

    # បំពេញប្រវែង top_row និង sub_row ឱ្យស្មើ num_cols
    top_row = (top_row + [""] * num_cols)[:num_cols]
    sub_row = (sub_row + [""] * num_cols)[:num_cols]

    # រៀបចំ Header Row 1 (ក្រុមធំ) និង Header Row 2 (ឈ្មោះកូន)
    # ជួរឈរ index 0..4 (ល.ស, ល.រ, គោត្តនាម-នាម, ភេទ, ឋានៈ) ប្រើ rowspan="2" ប្រសិនបើ sub_row ទទេ
    th_row1_html = []
    th_row2_html = []

    i = 0
    while i < num_cols:
        t_val = "" if "Unnamed" in top_row[i] else top_row[i]
        b_val = "" if "Unnamed" in sub_row[i] else sub_row[i]

        # ពិនិត្យមើលថាតើក្រុមធំ (top_row) មានបន្តទៅ Column បន្ទាប់ (colspan) ឬទេ
        if t_val and (i + 1 < num_cols) and (top_row[i + 1] == t_val or str(top_row[i + 1]).startswith("Unnamed")):
            span = 1
            j = i + 1
            while j < num_cols:
                next_t = top_row[j]
                next_b = "" if "Unnamed" in sub_row[j] else sub_row[j]
                # រាប់បញ្ចូល Column កូនដែលស្ថិតក្រោមក្រុមធំដូចគ្នា (ឬជា Unnamed ក្រោមក្រុមនោះ)
                if next_t == t_val or (str(next_t).startswith("Unnamed") and next_b in ("បានប្រើ", "នៅសល់", "")):
                    span += 1
                    j += 1
                else:
                    break

            if span > 1:
                th_row1_html.append(f'<th colspan="{span}" class="gs-group-th">{t_val}</th>')
                for k in range(i, i + span):
                    sub_label = "" if "Unnamed" in sub_row[k] else sub_row[k]
                    cls = "gs-sub-th gs-narrow" if sub_label in ("បានប្រើ", "នៅសល់") else "gs-sub-th"
                    th_row2_html.append(f'<th class="{cls}">{sub_label}</th>')
                i += span
                continue

        # ករណីជួរឈរធម្មតា (មិនមានកូនបំបែក)
        label = t_val or b_val or f"Col {i+1}"
        cls = "gs-main-th gs-narrow" if label in ("បានប្រើ", "នៅសល់", "ល.រ", "ភេទ") else "gs-main-th"
        th_row1_html.append(f'<th rowspan="2" class="{cls}">{label}</th>')
        i += 1

    # បង្កើតជួរដេកទិន្នន័យ (Body Rows)
    body_rows_html = []
    for _, row in body_df.iterrows():
        vals = [("" if pd.isna(v) or str(v).strip().lower() == "nan" else str(v).strip()) for v in row.tolist()]
        non_empty = [v for v in vals if v != ""]
        if not non_empty:
            continue

        # ពិនិត្យមើលថាតើជាជួរចំណងជើងផ្នែក ដូចជា "I. ថ្នាក់ដឹកនាំ" ឬ "II. ការិយាល័យ"
        first_non_empty = non_empty[0]
        is_section_row = (
            first_non_empty.startswith(("I.", "II.", "III.", "IV.", "V."))
            and len(non_empty) <= 2
        )

        if is_section_row:
            body_rows_html.append(
                f'<tr class="gs-section-row"><td colspan="{num_cols}">{first_non_empty}</td></tr>'
            )
        else:
            tds = []
            for idx, val in enumerate(vals):
                align_cls = "gs-center" if val in ("ប្រុស", "ស្រី", "-") or val.isdigit() else "gs-left"
                tds.append(f'<td class="{align_cls}">{val}</td>')
            body_rows_html.append(f'<tr>{"".join(tds)}</tr>')

    html = f"""
    <style>
      .gs-wrapper {{
        max-height: {max_height};
        overflow: auto;
        border: 1px solid #c7ccd1;
        border-radius: 4px;
        background: #ffffff;
        font-family: "Khmer OS Battambang", "Noto Sans Khmer", Arial, sans-serif;
        font-size: 13px;
      }}
      table.gs-table {{
        border-collapse: collapse;
        width: max-content;
        min-width: 100%;
        color: #1f2328;
      }}
      table.gs-table th, table.gs-table td {{
        border: 1px solid #d0d7de;
        padding: 5px 8px;
        white-space: nowrap;
        vertical-align: middle;
      }}
      table.gs-table thead th {{
        position: sticky;
        background-color: #eef3f8;
        font-weight: 700;
        text-align: center;
        z-index: 2;
      }}
      table.gs-table thead tr:nth-child(1) th {{
        top: 0;
        background-color: #e2ebf5;
      }}
      table.gs-table thead tr:nth-child(2) th {{
        top: 29px;
        background-color: #f1f5f9;
      }}
      table.gs-table th.gs-narrow, table.gs-table td.gs-narrow {{
        width: 56px;
        max-width: 68px;
        padding-left: 4px;
        padding-right: 4px;
        text-align: center;
      }}
      table.gs-table td.gs-center {{
        text-align: center;
      }}
      table.gs-table td.gs-left {{
        text-align: left;
      }}
      table.gs-table tr:hover td {{
        background-color: #f8fafc;
      }}
      table.gs-table tr.gs-section-row td {{
        background-color: #e8eef5;
        font-weight: 700;
        color: #0f172a;
        text-align: left;
        padding: 6px 10px;
      }}
    </style>
    <div class="gs-wrapper">
      <table class="gs-table">
        <thead>
          <tr>{"".join(th_row1_html)}</tr>
          <tr>{"".join(th_row2_html)}</tr>
        </thead>
        <tbody>
          {"".join(body_rows_html)}
        </tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


try:
    # អាន raw CSV ដោយមិនកំណត់ header ជាមុន ដើម្បីរក្សាទម្រង់ជួរដូច Google Sheet
    raw_df = pd.read_csv(csv_url, header=None)

    # រៀបចំ DataFrame សម្រាប់ស្វែងរកឈ្មោះ និង filter តាមបុគ្គលិក
    df = pd.read_csv(csv_url, header=[2, 3])
    merged_cols = []
    last_group = ""
    for i, (top, bottom) in enumerate(df.columns):
        t = "" if "Unnamed" in str(top) else str(top).strip()
        b = "" if "Unnamed" in str(bottom) else str(bottom).strip()
        if t:
            last_group = t
        if t and b and t != b:
            col_name = f"{t} - {b}"
        elif b in ("បានប្រើ", "នៅសល់") and last_group:
            col_name = f"{last_group} - {b}"
        else:
            col_name = b or t
        merged_cols.append(col_name or f"ជួរឈរ {i+1}")

    seen = {}
    unique_cols = []
    for col in merged_cols:
        if col in seen:
            seen[col] += 1
            unique_cols.append(f"{col} ({seen[col]})")
        else:
            seen[col] = 1
            unique_cols.append(col)
    df.columns = unique_cols
    df = df.dropna(how="all").reset_index(drop=True)

    name_col = next((c for c in ["គោត្តនាម-នាម", "ឈ្មោះ", "Name"] if c in df.columns), None)
    role_col = next((c for c in ["ឋានៈ", "តួនាទី", "Status"] if c in df.columns), None)

    # ==========================================
    # ផ្នែកទី ១៖ លទ្ធផលតាមឈ្មោះ (នៅខាងលើ)
    # ==========================================
    st.subheader("លទ្ធផលតាមឈ្មោះ")

    if name_col:
        names = (
            df[name_col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )
        names = [n for n in names if not n.startswith(("I.", "II.", "III.", "IV.", "V."))]

        if names:
            selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)
            filtered_df = df[df[name_col].astype(str).str.strip() == selected_name]

            if role_col and not filtered_df.empty:
                st.write(f"{role_col}:", filtered_df[role_col].iloc[0])

            # បង្ហាញជួររបស់បុគ្គលិកដែលបានជ្រើសរើសជាទម្រង់តារាងស្រដៀង Google Sheet
            if not filtered_df.empty:
                single_raw = pd.concat([raw_df.iloc[:4], raw_df[raw_df.isin([selected_name]).any(axis=1)]], ignore_index=True)
                render_sheet_like_table(single_raw, max_height="180px")
        else:
            st.info("មិនមានឈ្មោះបុគ្គលិកសម្រាប់បង្ហាញទេ។")
    else:
        st.warning("រកមិនឃើញជួរឈរឈ្មោះនៅក្នុង Sheet ទេ។")

    st.divider()

    # ==========================================
    # ផ្នែកទី ២៖ ទិន្នន័យទាំងអស់ (នៅខាងក្រោម)
    # ==========================================
    st.subheader("ទិន្នន័យទាំងអស់")
    st.write(f"ចំនួនជួរដេកសរុប (Total rows): {len(df)}")
    render_sheet_like_table(raw_df, max_height="500px")

except Exception as e:
    st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
