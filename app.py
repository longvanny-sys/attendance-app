import pandas as pd
import streamlit as st

st.set_page_config(page_title="បញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦", layout="wide")

st.title("តារាងបញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦ សាខា ប.ស.ស. ខេត្តពោធិ៍សាត់")

csv_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/export?format=csv&gid=2089000004"


def render_employee_leave_card(row_series: pd.Series):
    """បង្ហាញ Card សង្ខេប ៣ ជួរដូចរូបគំរូ"""
    def clean_cell(idx, default=""):
        if idx >= len(row_series):
            return default
        val = row_series.iloc[idx]
        if pd.isna(val):
            return default
        s = str(val).strip()
        return default if s == "" or s.lower() == "nan" else s

    # តាមលំដាប់ Column ក្នុង Sheet:
    # 0: ល.ស, 1: ល.រ, 2: គោត្តនាម-នាម, 3: ភេទ, 4: ឋានៈ
    # 5: P បានប្រើ, 6: P នៅសល់, 7: S បានប្រើ, 8: S នៅសល់, 9: SL បានប្រើ, 10: SL នៅសល់
    emp_name = clean_cell(2, "-")
    emp_gender = clean_cell(3, "-")
    emp_role = clean_cell(4, "-")

    p_used = clean_cell(5, "00")
    p_rem = clean_cell(6, "00")
    s_used = clean_cell(7, "00")
    s_rem = clean_cell(8, "00")
    sl_used = clean_cell(9, "00")
    sl_rem = clean_cell(10, "00")

    card_html = f"""
    <style>
      table.leave-card {{
        border-collapse: collapse;
        width: 100%;
        max-width: 820px;
        margin-top: 8px;
        margin-bottom: 12px;
        font-family: "Khmer OS Battambang", "Noto Sans Khmer", Arial, sans-serif;
        font-size: 15px;
        border: 2px solid #1f2328;
        background: #ffffff;
      }}
      table.leave-card th, table.leave-card td {{
        border: 1px solid #333333;
        padding: 7px 12px;
        text-align: center;
        vertical-align: middle;
      }}
      .lc-name {{
        background-color: #ffff00 !important;
        color: #4a148c !important;
        font-weight: 700;
        font-size: 16px;
        min-width: 150px;
      }}
      .lc-gender {{
        background-color: #f8cba6 !important;
        color: #1f2328 !important;
        font-weight: 700;
        width: 75px;
      }}
      .lc-role {{
        background-color: #f8cba6 !important;
        color: #1f2328 !important;
        font-weight: 700;
        min-width: 180px;
      }}
      .lc-p {{
        background-color: #009944 !important;
        color: #000000 !important;
        font-weight: 700;
        min-width: 120px;
      }}
      .lc-s {{
        background-color: #ffcc00 !important;
        color: #000000 !important;
        font-weight: 700;
        min-width: 120px;
      }}
      .lc-sl {{
        background-color: #e67300 !important;
        color: #000000 !important;
        font-weight: 700;
        min-width: 120px;
      }}
      .lc-label {{
        background-color: #ffffff !important;
        color: #111111 !important;
        font-weight: 700;
        text-align: right !important;
        padding-right: 18px !important;
      }}
      .lc-num {{
        background-color: #ffffff !important;
        color: #4a2c82 !important;
        font-weight: 700;
      }}
    </style>
    <table class="leave-card">
      <thead>
        <tr>
          <th colspan="2" class="lc-name">{emp_name}</th>
          <th class="lc-gender">{emp_gender}</th>
          <th class="lc-role">{emp_role}</th>
          <th class="lc-p">ប្រចាំឆ្នាំ (P)</th>
          <th class="lc-s">រយៈពេលខ្លី (S)</th>
          <th class="lc-sl">ឈឺ (SL)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td colspan="4" class="lc-label">ចំនួនថ្ងៃបានប្រើប្រាស់</td>
          <td class="lc-num">{p_used}</td>
          <td class="lc-num">{s_used}</td>
          <td class="lc-num">{sl_used}</td>
        </tr>
        <tr>
          <td colspan="4" class="lc-label">ចំនួនថ្ងៃនៅសល់</td>
          <td class="lc-num">{p_rem}</td>
          <td class="lc-num">{s_rem}</td>
          <td class="lc-num">{sl_rem}</td>
        </tr>
      </tbody>
    </table>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_sheet_like_table(raw_df: pd.DataFrame, max_height: str = "460px"):
    """បង្ហាញតារាងទាំងអស់ជាទម្រង់ស្រដៀង Google Sheet"""
    top_row = raw_df.iloc[2].fillna("").astype(str).str.strip().tolist() if len(raw_df) > 2 else []
    sub_row = raw_df.iloc[3].fillna("").astype(str).str.strip().tolist() if len(raw_df) > 3 else []
    body_df = raw_df.iloc[4:].dropna(how="all").reset_index(drop=True)
    num_cols = body_df.shape[1]

    top_row = (top_row + [""] * num_cols)[:num_cols]
    sub_row = (sub_row + [""] * num_cols)[:num_cols]

    col_classes = {}
    for idx in range(num_cols):
        t_clean = "" if "Unnamed" in top_row[idx] else top_row[idx]
        b_clean = "" if "Unnamed" in sub_row[idx] else sub_row[idx]
        combined = f"{t_clean} {b_clean}".strip()

        if "ល.រ" in combined or idx == 1:
            col_classes[idx] = "gs-col-tiny"
        elif "ល.ស" in combined or idx == 0:
            col_classes[idx] = "gs-col-tiny"
        elif "ភេទ" in combined or idx == 3:
            col_classes[idx] = "gs-col-small"
        elif "គោត្តនាម" in combined or idx == 2:
            col_classes[idx] = "gs-col-name"
        elif "ឋានៈ" in combined or idx == 4:
            col_classes[idx] = "gs-col-role"
        else:
            col_classes[idx] = "gs-col-compact"

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
                th_row1_html.append(f'<th colspan="{span}" class="gs-group-compact">{t_val}</th>')
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
      table.gs-table th.gs-col-tiny, table.gs-table td.gs-col-tiny {{
        width: 40px;
        min-width: 40px;
        max-width: 46px;
        padding-left: 2px;
        padding-right: 2px;
      }}
      table.gs-table th.gs-col-small, table.gs-table td.gs-col-small {{
        width: 52px;
        min-width: 52px;
        max-width: 60px;
        padding-left: 3px;
        padding-right: 3px;
      }}
      table.gs-table th.gs-col-compact, table.gs-table td.gs-col-compact {{
        width: 64px;
        min-width: 64px;
        max-width: 78px;
        padding-left: 3px;
        padding-right: 3px;
      }}
      table.gs-table th.gs-col-name, table.gs-table td.gs-col-name {{
        width: 135px;
        min-width: 135px;
        max-width: 160px;
        white-space: nowrap;
      }}
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

    st.subheader("លទ្ធផលតាមឈ្មោះ")
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
        names = [n for n in names if not n.startswith(("I.", "II.", "III.", "IV.", "V."))]

        if names:
            col_pick, _ = st.columns([1.2, 2.8])
            with col_pick:
                selected_name = st.selectbox("ជ្រើសរើសឈ្មោះ", names)

            matched_raw_rows = raw_df[
                raw_df.apply(lambda r: selected_name in [str(x).strip() for x in r.values], axis=1)
            ]

            if not matched_raw_rows.empty:
                render_employee_leave_card(matched_raw_rows.iloc[0])
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
