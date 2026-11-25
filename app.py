import pandas as pd
import streamlit as st

st.set_page_config(page_title="បញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦", layout="wide")

st.title("តារាងបញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦ សាខា ប.ស.ស. ខេត្តពោធិ៍សាត់")

csv_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/export?format=csv&gid=2089000004"


def render_sheet_like_table(raw_df: pd.DataFrame, max_height: str = "460px"):
    """បង្ហាញតារាងជាទម្រង់ស្រដៀង Google Sheet ដោយបង្រួម column ធំៗឱ្យតូចទាំងអស់"""
    top_row = raw_df.iloc[2].fillna("").astype(str).str.strip().tolist() if len(raw_df) > 2 else []
    sub_row = raw_df.iloc[3].fillna("").astype(str).str.strip().tolist() if len(raw_df) > 3 else []

    body_df = raw_df.iloc[4:].dropna(how="all").reset_index(drop=True)
    num_cols = body_df.shape[1]

    top_row = (top_row + [""] * num_cols)[:num_cols]
    sub_row = (sub_row + [""] * num_cols)[:num_cols]

    # កំណត់ប្រភេទទទឹងតាម column index ឬឈ្មោះ column
    col_classes = {}
    for idx in range(num_cols):
        t_clean = "" if "Unnamed" in top_row[idx] else top_row[idx]
        b_clean = "" if "Unnamed" in sub_row[idx] else sub_row[idx]
        combined = f"{t_clean} {b_clean}".strip()

        if "ល.រ" in combined or idx == 1:
            col_classes[idx] = "gs-col-tiny"       # ល.រ (តូចបំផុត)
        elif "ល.ស" in combined or idx == 0:
            col_classes[idx] = "gs-col-tiny"       # ល.ស (តូចបំផុត)
        elif "ភេទ" in combined or idx == 3:
            col_classes[idx] = "gs-col-small"      # ភេទ
        elif "គោត្តនាម" in combined or idx == 2:
            col_classes[idx] = "gs-col-name"       # ឈ្មោះ (ទទឹងល្មមអានច្បាស់)
        elif "ឋានៈ" in combined or idx == 4:
            col_classes[idx] = "gs-col-role"       # ឋានៈ (ចុះបន្ទាត់បាន មិនរីកធំពេក)
        else:
            col_classes[idx] = "gs-col-compact"    # ជួរឈរច្បាប់ និងលេខផ្សេងៗ (បង្រួមឱ្យតូច)

    th_row1_html = []
    th_row2_html = []

    i = 0
    while i < num_cols:
        t_val = "" if "Unnamed" in top_row[i] else top_row[i]
        b_val = "" if "Unnamed" in sub_row[i] else sub_row[i]

        if t_val and (i + 1 < num_cols) and (top_row[i + 1] == t_val or str(top_row[i + 1]).startswith("Unnamed")):
            span = 1
            j = i + 1
            while j < num_cols:
                next_t = top_row[j]
                next_b = "" if "Unnamed" in sub_row[j] else sub_row[j]
                if next_t == t_val or (str(next_t).startswith("Unnamed") and next_b in ("បានប្រើ", "នៅសល់", "")):
                    span += 1
                    j += 1
                else:
                    break

            if span > 1:
                # ប្រើ class តូចសម្រាប់ក្រុមធំដែលមានកូនច្រើន ដើម្បីកុំឱ្យរីកធំពេក
                group_cls = "gs-group-compact"
                th_row1_html.append(f'<th colspan="{span}" class="{group_cls}">{t_val}</th>')
                for k in range(i, i + span):
                    sub_label = "" if "Unnamed" in sub_row[k] else sub_row[k]
                    c_cls = col_classes.get(k, "gs-col-compact")
                    th_row2_html.append(f'<th class="{c_cls}">{sub_label}</th>')
                i += span
                continue

        label = t_val or b_val or f"Col {i+1}"
        c_cls = col_classes.get(i, "gs-col-compact")
        th_row1_html.append(f'<th rowspan="2" class="{c_cls}">{label}</th>')
        i += 1

    body_rows_html = []
    for _, row in body_df.iterrows():
        vals = [("" if pd.isna(v) or str(v).strip().lower() == "nan" else str(v).strip()) for v in row.tolist()]
        non_empty = [v for v in vals if v != ""]
        if not non_empty:
            continue

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
                c_cls = col_classes.get(idx, "gs-col-compact")
                if c_cls in ("gs-col-tiny", "gs-col-small", "gs-col-compact"):
                    tds.append(f'<td class="{c_cls} gs-center">{val}</td>')
                else:
                    tds.append(f'<td class="{c_cls} gs-left">{val}</td>')
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
        font-size: 12.5px;
      }}
      table.gs-table {{
        border-collapse: collapse;
        width: auto;
        table-layout: fixed;
        color: #1f2328;
      }}
      table.gs-table th, table.gs-table td {{
        border: 1px solid #d0d7de;
        padding: 4px 5px;
        vertical-align: middle;
        overflow-wrap: anywhere;
        word-break: break-word;
      }}
      table.gs-table thead th {{
        position: sticky;
        background-color: #eef3f8;
        font-weight: 700;
        text-align: center;
        white-space: normal;
        line-height: 1.25;
        z-index: 2;
      }}
      table.gs-table thead tr:nth-child(1) th {{
        top: 0;
        background-color: #e2ebf5;
      }}
      table.gs-table thead tr:nth-child(2) th {{
        top: 30px;
        background-color: #f1f5f9;
      }}
      /* ទទឹងតូចបំផុតសម្រាប់ ល.ស និង ល.រ */
      table.gs-table th.gs-col-tiny, table.gs-table td.gs-col-tiny {{
        width: 40px;
        min-width: 40px;
        max-width: 46px;
        padding-left: 2px;
        padding-right: 2px;
      }}
      /* ទទឹងតូចសម្រាប់ ភេទ */
      table.gs-table th.gs-col-small, table.gs-table td.gs-col-small {{
        width: 52px;
        min-width: 52px;
        max-width: 60px;
        padding-left: 3px;
        padding-right: 3px;
      }}
      /* ទទឹងបង្រួមសម្រាប់ជួរឈរច្បាប់ និងលេខផ្សេងៗ */
      table.gs-table th.gs-col-compact, table.gs-table td.gs-col-compact {{
        width: 64px;
        min-width: 90px;
        max-width: 78px;
        padding-left: 3px;
        padding-right: 3px;
      }}
      /* ទទឹងសមរម្យសម្រាប់ឈ្មោះបុគ្គលិក */
      table.gs-table th.gs-col-name, table.gs-table td.gs-col-name {{
        width: 135px;
        min-width: 135px;
        max-width: 160px;
        white-space: nowrap;
      }}
      /* ទទឹងសមរម្យសម្រាប់ឋានៈ (អនុញ្ញាតឱ្យចុះបន្ទាត់បាន មិនរីកធំពេក) */
      table.gs-table th.gs-col-role, table.gs-table td.gs-col-role {{
        width: 155px;
        min-width: 155px;
        max-width: 190px;
        white-space: normal;
        line-height: 1.25;
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
        white-space: normal;
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
    raw_df = pd.read_csv(csv_url, header=None)

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
    # ផ្នែកទី ១៖ លទ្ធផលតាមឈ្មោះ (នៅខាងលើ)
    # ==========================================
    st.subheader("លទ្ធផលតាមឈ្មោះ")

    # បង្រួមទទឹង selectbox «ជ្រើសរើសឈ្មោះ» ឱ្យខ្លីល្មម (ប្រើ column 1 ក្នុងចំណោម 3 ផ្នែក)
    st.markdown(
        """
        <style>
          div[data-testid="stSelectbox"] {
            max-width: 280px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
      names = [
          n
          for n in names
          if not n.startswith(("I.", "II.", "III.", "IV.", "V."))
      ]

      if names:
        col_pick, _ = st.columns([1.2, 2.8])
        with col_pick:
          selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)

        filtered_df = df[df[name_col].astype(str).str.strip() == selected_name]

        if role_col and not filtered_df.empty:
          st.write(f"{role_col}:", filtered_df[role_col].iloc[0])

        if not filtered_df.empty:
          single_raw = pd.concat(
              [
                  raw_df.iloc[:4],
                  raw_df[raw_df.isin([selected_name]).any(axis=1)],
              ],
              ignore_index=True,
          )
          render_sheet_like_table(single_raw, max_height="180px")
      else:
        st.info("មិនមានឈ្មោះបុគ្គលិកសម្រាប់បង្ហាញទេ។")
    else:
      st.warning("រកមិនឃើញជួរឈរឈ្មោះនៅក្នុង Sheet ទេ។")

    st.divider()

    st.subheader("ទិន្នន័យទាំងអស់")
    st.write(f"ចំនួនជួរដេកសរុប (Total rows): {len(df)}")
    render_sheet_like_table(raw_df, max_height="500px")

except Exception as e:
    st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
