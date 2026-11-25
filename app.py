import re
import textwrap
import pandas as pd
import streamlit as st

st.set_page_config(page_title="បញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦", layout="wide")

st.title("តារាងបញ្ជីវត្តមានសរុបប្រចាំឆ្នាំ២០២៦ សាខា ប.ស.ស. ខេត្តពោធិ៍សាត់")

SPREADSHEET_ID = "1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE"
SUMMARY_GID = "2089000004"
csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    f"/export?format=csv&gid={SUMMARY_GID}"
)

# កំណត់ index ជួរឈរ (ចាប់ផ្តើមពី 0) សម្រាប់ "ច្បាប់..." នៅខាងលើនៃ Card
QUOTA_COLS = {
    "P": 5,
    "S": 7,
    "SL": 9,
}

# ប្រសិនបើចង់បង្ខំ index ជួរឈរសម្រាប់ "នៅសល់" ផ្ទាល់ អាចកំណត់លេខជួរឈរ (0, 1, 2...)
# ប្រសិនបើដាក់ None កម្មវិធីនឹងស្វែងរកជួរឈរដែលមានពាក្យ "នៅសល់" ដោយស្វ័យប្រវត្តិ
MANUAL_REMAINING_COLS = {
    "P": 6,
    "S": 8,
    "SL": 10,
}

# កំណត់បញ្ជីខែ និង gid នៃ Sheet ខែនីមួយៗ (4-26 ដល់ 3-27)
MONTH_SHEETS = [
    {"label": "មេសា ២០២៦", "sheet": "4-26", "gid": "1974334752"},
    {"label": "ឧសភា ២០២៦", "sheet": "5-26", "gid": "1765643733"},
    {"label": "មិថុនា ២០២៦", "sheet": "6-26", "gid": "709324239"},
    {"label": "កក្កដា ២០២៦", "sheet": "7-26", "gid": "558720548"},
    {"label": "សីហា ២០២៦", "sheet": "8-26", "gid": "1537765030"},
    {"label": "កញ្ញា ២០២៦", "sheet": "9-26", "gid": "1812889418"},
    {"label": "តុលា ២០២៦", "sheet": "10-26", "gid": "309255693"},
    {"label": "វិច្ឆិកា ២០២៦", "sheet": "11-26", "gid": "1707699913"},
    {"label": "ធ្នូ ២០២៦", "sheet": "12-26", "gid": "485167717"},
    {"label": "មករា ២០២៧", "sheet": "1-27", "gid": "1361878427"},
    {"label": "កុម្ភៈ ២០២៧", "sheet": "2-27", "gid": "1002610773"},
    {"label": "មីនា ២០២៧", "sheet": "3-27", "gid": "1749336699"},
]

# អក្សរសម្គាល់ដែលត្រូវរាប់ (ប្រើ Nf តែមួយមុខ)
TARGET_CODES = ["P", "S", "SL", "Nf", "ML", "V", "X", "កបន"]

KHMER_DIGITS = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")
ARABIC_DIGITS = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")


def get_expected_credentials():
    """ទាញ Username និង Password ពី secrets.toml ឬប្រើតម្លៃបម្រុង"""
    try:
        auth_cfg = st.secrets.get("auth", {})
        user_val = str(auth_cfg.get("username", "admin")).strip()
        pass_val = str(auth_cfg.get("password", "123456")).strip()
        return user_val, pass_val
    except Exception:
        return "admin", "123456"


def render_login_lock_box():
    """បង្ហាញប្រអប់ Login ចាក់សោចាប់ពីតារាងប្រចាំខែចុះក្រោម"""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "logged_user" not in st.session_state:
        st.session_state["logged_user"] = ""

    if st.session_state["logged_in"]:
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.success(f"បានចូលប្រើប្រាស់ក្នុងនាម៖ **{st.session_state['logged_user']}**")
        with col_btn:
            if st.button("ចាកចេញ (Logout)", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state["logged_user"] = ""
                st.rerun()
        return True

    st.info("🔒 ចាប់ពីតារាងប្រចាំខែចុះក្រោមត្រូវបានចាក់សោ។ សូមបញ្ចូលគណនីដើម្បីបង្ហាញ។")

    expected_user, expected_pass = get_expected_credentials()

    with st.form("login_lock_form", clear_on_submit=False):
        input_user = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)")
        input_pass = st.text_input("ពាក្យសម្ងាត់ (Password)", type="password")
        submitted = st.form_submit_button("ចូលប្រើប្រាស់ (Login)")

        if submitted:
            if input_user.strip() == expected_user and input_pass == expected_pass:
                st.session_state["logged_in"] = True
                st.session_state["logged_user"] = input_user.strip()
                st.rerun()
            else:
                st.error("ឈ្មោះអ្នកប្រើប្រាស់ ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ។")

    return False


def strip_invisible(text: str) -> str:
    """លុបអក្សរលាក់ ដូចជា U+200B ដែលបង្កបញ្ហាពេល Copy/Paste"""
    return re.sub(r"[\u200b-\u200f\ufeff]", "", str(text))


def to_khmer_num(val_str: str) -> str:
    """ប្តូរលេខអារ៉ាប់ទៅជាលេខខ្មែរ"""
    return strip_invisible(val_str).translate(KHMER_DIGITS)


def format_count_val(val: float) -> str:
    """បំប្លែងចំនួនរាប់ (ចំនួនគត់ ឬ ទសភាគ) ទៅជាលេខខ្មែរ"""
    if abs(val - round(val)) < 1e-9:
        return to_khmer_num(str(int(round(val))))
    formatted = f"{val:.2f}".rstrip("0").rstrip(".")
    return to_khmer_num(formatted)


def format_pel_value(raw_val, default_zero: bool = True) -> str:
    """បំប្លែងតម្លៃទៅជាទម្រង់លេខខ្មែរ + ពេល (ដូចជា ១៨ ពេល ឬ ០០ ពេល)"""
    if pd.isna(raw_val):
        return "០០ ពេល" if default_zero else "-"
    s = strip_invisible(raw_val).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return "០០ ពេល" if default_zero else "-"
    if s in ("-", "–", "—"):
        return "-"

    s_ascii = s.translate(ARABIC_DIGITS)
    try:
        num = float(s_ascii)
        if num.is_integer():
            n_int = int(num)
            if n_int == 0 and s_ascii.startswith("00"):
                return "០០ ពេល"
            return f"{to_khmer_num(str(n_int))} ពេល"
        return f"{to_khmer_num(s_ascii)} ពេល"
    except ValueError:
        cleaned = to_khmer_num(s)
        if "ពេល" not in cleaned:
            return f"{cleaned} ពេល"
        return cleaned


def detect_remaining_columns(df: pd.DataFrame) -> dict:
    """ស្វែងរក index ជួរឈរដែលមានពាក្យ 'នៅសល់' សម្រាប់ P, S, SL"""
    detected = {"P": None, "S": None, "SL": None}
    if df.empty:
        return detected

    header_rows = df.iloc[: min(6, len(df))]
    col_labels = {}

    for col_idx in range(df.shape[1]):
        texts = []
        for _, r_val in header_rows.iloc[:, col_idx].items():
            if pd.notna(r_val):
                t = strip_invisible(r_val).strip()
                if t and t.lower() not in ("none", "nan"):
                    texts.append(t)
        col_labels[col_idx] = " ".join(texts)

    for col_idx, label_text in col_labels.items():
        if "នៅសល់" not in label_text:
            continue
        low = label_text.lower()
        if detected["P"] is None and ("(p)" in low or "ប្រចាំឆ្នាំ" in label_text):
            detected["P"] = col_idx
        elif detected["S"] is None and ("(s)" in low or "រយៈពេលខ្លី" in label_text):
            detected["S"] = col_idx
        elif detected["SL"] is None and ("(sl)" in low or "ឈឺ" in label_text):
            detected["SL"] = col_idx

    rem_cols = [idx for idx, txt in col_labels.items() if "នៅសល់" in txt]
    codes_order = ["P", "S", "SL"]
    for pos, code in enumerate(codes_order):
        if detected[code] is None and pos < len(rem_cols):
            detected[code] = rem_cols[pos]

    return detected


def get_remaining_val_from_summary(
    row_series: pd.Series, code: str, detected_cols: dict
) -> str:
    """ទាញតម្លៃច្បាប់នៅសល់ផ្ទាល់ពី Sheet សង្ខេប"""
    manual_idx = MANUAL_REMAINING_COLS.get(code)
    col_idx = manual_idx if manual_idx is not None else detected_cols.get(code)

    if col_idx is not None and col_idx < len(row_series):
        return format_pel_value(row_series.iloc[col_idx], default_zero=False)

    fallback_map = {"P": 6, "S": 8, "SL": 10}
    fb_idx = fallback_map.get(code)
    if fb_idx is not None and fb_idx < len(row_series):
        return format_pel_value(row_series.iloc[fb_idx], default_zero=False)

    return "-"


@st.cache_data(ttl=120)
def load_csv_cached(url: str):
    try:
        df = pd.read_csv(url, header=None)
        return df, None
    except Exception as exc:
        return pd.DataFrame(), str(exc)


@st.cache_data(ttl=120)
def load_month_sheet_by_gid(spreadsheet_id: str, gid: str):
    clean_gid = strip_invisible(gid).strip()
    if not clean_gid:
        return pd.DataFrame(), "មិនទាន់បានបំពេញ gid"
    month_url = (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        f"/export?format=csv&gid={clean_gid}"
    )
    try:
        df = pd.read_csv(month_url, header=None)
        return df, None
    except Exception as exc:
        return pd.DataFrame(), str(exc)


def normalize_name(name_str: str) -> str:
    """សម្អាតអក្សរលាក់ ដកឃ្លាស្ទួន និងដកឃ្លាក្បាល/កន្ទុយ"""
    cleaned = strip_invisible(name_str)
    return " ".join(cleaned.strip().split())


def parse_token_weight(tok: str):
    """ទាញយក (ឈ្មោះកូដ, ចំនួន) ពី token ដូចជា P, 0.5P, 1/2SL, កបន"""
    tok_clean = strip_invisible(tok).strip().translate(ARABIC_DIGITS)
    if not tok_clean:
        return None

    upper_map = {
        "P": "P",
        "S": "S",
        "SL": "SL",
        "NF": "Nf",
        "ML": "ML",
        "V": "V",
        "X": "X",
        "កបន": "កបន",
    }

    if tok_clean in TARGET_CODES:
        return tok_clean, 1.0
    if tok_clean.upper() in upper_map:
        return upper_map[tok_clean.upper()], 1.0

    match = re.fullmatch(
        r"^(?:(\d+(?:\.\d+)?)|(\d+)/(\d+))?\s*([A-Za-z]+|កបន)$",
        tok_clean,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    dec_part, num_part, den_part, code_part = match.groups()
    mapped_code = upper_map.get(code_part.upper()) or upper_map.get(code_part)
    if not mapped_code:
        return None

    weight = 1.0
    if dec_part is not None:
        weight = float(dec_part)
    elif num_part is not None and den_part is not None and float(den_part) != 0:
        weight = float(num_part) / float(den_part)

    return mapped_code, weight


def count_employee_month_codes(month_df: pd.DataFrame, emp_name: str):
    """ស្វែងរកជួរដេករបស់បុគ្គលិកក្នុង Sheet ខែ ហើយរាប់ចំនួនអក្សរសម្គាល់"""
    counts = {code: 0.0 for code in TARGET_CODES}
    if month_df.empty or not emp_name:
        return counts, 0

    target_norm = normalize_name(emp_name)
    matched_indices = []

    for idx, row in month_df.iterrows():
        row_norms = [
            normalize_name(v)
            for v in row.tolist()
            if pd.notna(v) and normalize_name(v) != ""
        ]
        if target_norm in row_norms:
            matched_indices.append(idx)

    if not matched_indices:
        return counts, 0

    for r_idx in matched_indices:
        row_vals = month_df.iloc[r_idx].tolist()
        for cell in row_vals:
            if pd.isna(cell):
                continue
            cell_str = normalize_name(cell)
            if not cell_str or cell_str.lower() == "nan":
                continue

            if cell_str == target_norm:
                continue

            tokens = [
                t.strip()
                for t in re.split(r"[/,;+\s]+", cell_str)
                if t.strip()
            ]
            for tok in tokens:
                parsed = parse_token_weight(tok)
                if parsed:
                    code_key, weight = parsed
                    counts[code_key] += weight

    return counts, len(matched_indices)


def compute_monthly_totals(emp_name: str, month_sheets: list, spreadsheet_id: str):
    """គណនាទិន្នន័យប្រចាំខែ និងផលបូកសរុបប្រចាំឆ្នាំ"""
    monthly_records = []
    totals = {code: 0.0 for code in TARGET_CODES}
    debug_rows = []

    for m in month_sheets:
        month_label = m.get("label", "")
        sheet_name = m.get("sheet", "")
        gid = m.get("gid", "")
        m_df, m_err = load_month_sheet_by_gid(spreadsheet_id, gid)
        c, match_count = count_employee_month_codes(m_df, emp_name)

        for k in TARGET_CODES:
            totals[k] += c[k]

        monthly_records.append({"label": month_label, "counts": c})
        debug_rows.append(
            {
                "ខែ": month_label,
                "Sheet": sheet_name,
                "gid": gid if gid else "(ទទេ)",
                "ស្ថានភាពទាញ": "ជោគជ័យ" if not m_df.empty else (m_err or "ទទេ"),
                "ជួរផ្គូផ្គងឈ្មោះ": match_count,
            }
        )

    return monthly_records, totals, debug_rows


def render_monthly_breakdown_table(monthly_records: list, totals: dict, debug_rows: list):
    """បង្ហាញតារាងសរុបប្រចាំខែតាមអក្សរសម្គាល់ ដោយ Fit ជាមួយអេក្រង់ទូរស័ព្ទ និង ខែ ធំជាងគេ"""
    rows_list = []

    for item in monthly_records:
        month_label = item["label"]
        c = item["counts"]

        def cell_disp(val: float) -> str:
            return "" if val <= 0 else format_count_val(val)

        row_html = (
            "<tr>"
            f'<td class="mb-month">{month_label}</td>'
            f'<td class="mb-num">{cell_disp(c["P"])}</td>'
            f'<td class="mb-num">{cell_disp(c["S"])}</td>'
            f'<td class="mb-num">{cell_disp(c["SL"])}</td>'
            f'<td class="mb-num">{cell_disp(c["Nf"])}</td>'
            f'<td class="mb-num">{cell_disp(c["ML"])}</td>'
            f'<td class="mb-num">{cell_disp(c["V"])}</td>'
            f'<td class="mb-num">{cell_disp(c["X"])}</td>'
            f'<td class="mb-num">{cell_disp(c["កបន"])}</td>'
            "</tr>"
        )
        rows_list.append(row_html)

    total_html = (
        '<tr class="mb-total-row">'
        '<td class="mb-month">សរុប</td>'
        f'<td class="mb-num">{format_count_val(totals["P"]) if totals["P"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["S"]) if totals["S"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["SL"]) if totals["SL"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["Nf"]) if totals["Nf"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["ML"]) if totals["ML"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["V"]) if totals["V"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["X"]) if totals["X"] > 0 else "-"}</td>'
        f'<td class="mb-num">{format_count_val(totals["កបន"]) if totals["កបន"] > 0 else "-"}</td>'
        "</tr>"
    )
    rows_list.append(total_html)

    table_html = textwrap.dedent(f"""
    <style>
    .mb-wrap {{
      width: 100%;
      max-width: 760px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      margin-top: 8px;
      margin-bottom: 16px;
      border-radius: 4px;
    }}
    table.mb-table {{
      border-collapse: collapse;
      table-layout: fixed;
      width: 100%;
      min-width: 540px;
      font-family: "Khmer OS Battambang", "Noto Sans Khmer", Arial, sans-serif;
      font-size: 11.5px;
      border: 1.5px solid #1f2328;
      background: #ffffff;
    }}
    col.mb-col-month {{ width: 23%; }}
    col.mb-col-main  {{ width: 12.5%; }}
    col.mb-col-other {{ width: 7.9%; }}

    table.mb-table th, table.mb-table td {{
      border: 1px solid #444444;
      padding: 4px 3px;
      text-align: center;
      vertical-align: middle;
      line-height: 1.3;
      word-break: normal;
      overflow-wrap: normal;
    }}
    table.mb-table th.mb-th-month,
    table.mb-table td.mb-month,
    table.mb-table th.mb-th-p,
    table.mb-table th.mb-th-s,
    table.mb-table th.mb-th-sl {{
      white-space: nowrap;
      font-size: 11px;
      padding: 4px 3px;
    }}
    table.mb-table th.mb-th-month,
    table.mb-table td.mb-month {{
      position: sticky;
      left: 0;
      z-index: 1;
    }}
    table.mb-table th.mb-th-month {{
      z-index: 2;
    }}
    .mb-th-month {{
      background-color: #d9d9d9 !important;
      color: #000000 !important;
      font-weight: 700;
    }}
    .mb-th-p {{ background-color: #009944 !important; color: #000000 !important; font-weight: 700; }}
    .mb-th-s {{ background-color: #ffcc00 !important; color: #000000 !important; font-weight: 700; }}
    .mb-th-sl {{ background-color: #e67300 !important; color: #000000 !important; font-weight: 700; }}
    .mb-th-nf {{ background-color: #00b050 !important; color: #ffff00 !important; font-weight: 700; }}
    .mb-th-ml {{ background-color: #e6b8b7 !important; color: #000000 !important; font-weight: 700; }}
    .mb-th-v {{ background-color: #00b0f0 !important; color: #000000 !important; font-weight: 700; }}
    .mb-th-x {{ background-color: #31869b !important; color: #ffffff !important; font-weight: 700; }}
    .mb-th-kbn {{ background-color: #ff0000 !important; color: #ffff00 !important; font-weight: 700; }}
    td.mb-month {{
      background-color: #d9d9d9 !important;
      color: #000000 !important;
      font-weight: 700;
    }}
    td.mb-num {{
      background-color: #ffffff !important;
      color: #111111 !important;
      font-weight: 600;
      height: 26px;
    }}
    tr.mb-total-row td {{
      background-color: #f3f6fa !important;
      font-weight: 700;
      border-top: 2px solid #1f2328;
    }}
    tr.mb-total-row td.mb-month {{
      background-color: #d9d9d9 !important;
    }}

    @media (max-width: 640px) {{
      .mb-wrap {{
        max-width: 100%;
        margin-top: 6px;
        margin-bottom: 12px;
      }}
      table.mb-table {{
        min-width: 100%;
        font-size: 10px;
      }}
      col.mb-col-month {{ width: 26%; }}
      col.mb-col-main  {{ width: 11.5%; }}
      col.mb-col-other {{ width: 7.9%; }}
      table.mb-table th, table.mb-table td {{
        padding: 3px 1.5px;
        line-height: 1.25;
      }}
      table.mb-table th.mb-th-month,
      table.mb-table td.mb-month,
      table.mb-table th.mb-th-p,
      table.mb-table th.mb-th-s,
      table.mb-table th.mb-th-sl {{
        font-size: 9.5px;
        padding: 3px 2px;
      }}
      td.mb-num {{
        height: 24px;
      }}
    }}
    </style>
    <div class="mb-wrap">
    <table class="mb-table">
    <colgroup>
      <col class="mb-col-month">
      <col class="mb-col-main">
      <col class="mb-col-main">
      <col class="mb-col-main">
      <col class="mb-col-other">
      <col class="mb-col-other">
      <col class="mb-col-other">
      <col class="mb-col-other">
      <col class="mb-col-other">
    </colgroup>
    <thead>
    <tr>
    <th class="mb-th-month">ខែ</th>
    <th class="mb-th-p">ប្រចាំឆ្នាំ (P)</th>
    <th class="mb-th-s">រយៈពេលខ្លី (S)</th>
    <th class="mb-th-sl">ឈឺ (SL)</th>
    <th class="mb-th-nf">Nf</th>
    <th class="mb-th-ml">ML</th>
    <th class="mb-th-v">V</th>
    <th class="mb-th-x">X</th>
    <th class="mb-th-kbn">កបន</th>
    </tr>
    </thead>
    <tbody>
    {"".join(rows_list)}
    </tbody>
    </table>
    </div>
    """).strip()

    st.markdown(table_html, unsafe_allow_html=True)

    with st.expander("ពិនិត្យស្ថានភាពទាញទិន្នន័យតាមខែ (Debug)"):
        st.dataframe(pd.DataFrame(debug_rows), use_container_width=True)


def render_employee_leave_card(row_series: pd.Series, detected_cols: dict):
    """បង្ហាញ Card សង្ខេប និងទាញច្បាប់នៅសល់ផ្ទាល់ពី Sheet សង្ខេប"""

    def clean_text(idx, default="-"):
        if idx >= len(row_series):
            return default
        val = row_series.iloc[idx]
        if pd.isna(val):
            return default
        s = strip_invisible(val).strip()
        return default if s == "" or s.lower() in ("nan", "none") else to_khmer_num(s)

    def clean_pel(idx, default_zero=False):
        if idx is None or idx >= len(row_series):
            return "០០ ពេល" if default_zero else "-"
        return format_pel_value(row_series.iloc[idx], default_zero=default_zero)

    emp_id = clean_text(1, "-")
    emp_name = clean_text(2, "-")
    emp_gender = clean_text(3, "-")
    emp_role = clean_text(4, "-")

    leave_p = clean_pel(QUOTA_COLS.get("P"), default_zero=False)
    leave_s = clean_pel(QUOTA_COLS.get("S"), default_zero=False)
    leave_sl = clean_pel(QUOTA_COLS.get("SL"), default_zero=False)

    rem_p = get_remaining_val_from_summary(row_series, "P", detected_cols)
    rem_s = get_remaining_val_from_summary(row_series, "S", detected_cols)
    rem_sl = get_remaining_val_from_summary(row_series, "SL", detected_cols)

    card_html = textwrap.dedent(f"""
    <style>
    .emp-card {{
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 14px 16px;
      margin: 10px 0 14px 0;
      background-color: #f8fafc;
      max-width: 760px;
      font-family: "Khmer OS Battambang", "Noto Sans Khmer", Arial, sans-serif;
      color: #0f172a;
    }}
    .emp-card-title {{
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .emp-card-sub {{
      font-size: 13.5px;
      color: #334155;
      margin-bottom: 10px;
    }}
    .emp-card-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .emp-stat-box {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 8px 12px;
      min-width: 155px;
      flex: 1 1 140px;
    }}
    .emp-stat-label {{
      font-size: 12px;
      color: #64748b;
    }}
    .emp-stat-val {{
      font-size: 15px;
      font-weight: 700;
      color: #0f172a;
    }}
    .emp-stat-rem {{
      font-size: 13px;
      font-weight: 700;
      color: #0f766e;
      margin-top: 4px;
    }}
    @media (max-width: 640px) {{
      .emp-card {{
        padding: 11px 12px;
        margin: 8px 0 10px 0;
      }}
      .emp-card-title {{
        font-size: 14px;
      }}
      .emp-card-sub {{
        font-size: 12px;
      }}
      .emp-stat-box {{
        padding: 6px 9px;
        min-width: 0;
        flex: 1 1 calc(33.33% - 8px);
      }}
      .emp-stat-label {{
        font-size: 10px;
      }}
      .emp-stat-val {{
        font-size: 12px;
      }}
      .emp-stat-rem {{
        font-size: 10.5px;
      }}
    }}
    </style>
    <div class="emp-card">
    <div class="emp-card-title">ឈ្មោះ៖ {emp_name} ({emp_gender}) — អត្តលេខ៖ {emp_id}</div>
    <div class="emp-card-sub">តួនាទី៖ {emp_role}</div>
    <div class="emp-card-stats">
    <div class="emp-stat-box">
    <div class="emp-stat-label">ច្បាប់ប្រចាំឆ្នាំ (P)</div>
    <div class="emp-stat-val">{leave_p}</div>
    <div class="emp-stat-rem">នៅសល់៖ {rem_p}</div>
    </div>
    <div class="emp-stat-box">
    <div class="emp-stat-label">ច្បាប់រយៈពេលខ្លី (S)</div>
    <div class="emp-stat-val">{leave_s}</div>
    <div class="emp-stat-rem">នៅសល់៖ {rem_s}</div>
    </div>
    <div class="emp-stat-box">
    <div class="emp-stat-label">ច្បាប់ឈឺ (SL)</div>
    <div class="emp-stat-val">{leave_sl}</div>
    <div class="emp-stat-rem">នៅសល់៖ {rem_sl}</div>
    </div>
    </div>
    </div>
    """).strip()

    st.markdown(card_html, unsafe_allow_html=True)


def render_summary_overview_table(summary_df: pd.DataFrame):
    """បង្ហាញតារាង Sheet សង្ខេបទាំងមូល សមល្មមក្នុងទំព័រ និងទូរស័ព្ទ"""
    if summary_df.empty:
        st.info("គ្មានទិន្នន័យក្នុង Sheet សង្ខេបទេ។")
        return

    rows_html = []

    for _, row in summary_df.iterrows():
        vals = [
            ""
            if pd.isna(v) or strip_invisible(v).strip().lower() in ("", "none", "nan")
            else strip_invisible(v).strip()
            for v in row.tolist()
        ]

        if all(x == "" for x in vals):
            continue

        c0 = vals[0] if len(vals) > 0 else ""
        c1 = vals[1] if len(vals) > 1 else ""
        c2 = vals[2] if len(vals) > 2 else ""
        c3 = vals[3] if len(vals) > 3 else ""
        c4 = vals[4] if len(vals) > 4 else ""
        c5 = vals[5] if len(vals) > 5 else ""
        c6 = vals[6] if len(vals) > 6 else ""
        c7 = vals[7] if len(vals) > 7 else ""
        c8 = vals[8] if len(vals) > 8 else ""
        c9 = vals[9] if len(vals) > 9 else ""
        c10 = vals[10] if len(vals) > 10 else ""

        header_check = " ".join([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
        if any(
            k in header_check
            for k in (
                "គោត្តនាម",
                "បានប្រើ",
                "នៅសល់",
                "ច្បាប់ប្រចាំ",
                "ច្បាប់រយៈ",
                "ច្បាប់ឈឺ",
            )
        ):
            continue

        section_text = c0 or c2
        is_section_row = (
            section_text.startswith(("I.", "II.", "III.", "IV.", "V.", "១.", "២."))
            and not c3
            and not c4
            and not c5
            and not c6
        )

        if is_section_row:
            rows_html.append(
                f'<tr class="ov-section-row">'
                f'<td class="ov-sec-title" colspan="11">{to_khmer_num(section_text)}</td>'
                f"</tr>"
            )
            continue

        if not c2:
            continue

        def fmt_cell(val_str: str, dash_when_empty: bool = False) -> str:
            if not val_str:
                return "-" if dash_when_empty else ""
            if val_str in ("-", "–", "—"):
                return "-"
            return to_khmer_num(val_str)

        rows_html.append(
            "<tr>"
            f'<td class="ov-center">{fmt_cell(c0)}</td>'
            f'<td class="ov-center">{fmt_cell(c1)}</td>'
            f'<td class="ov-left ov-bold">{fmt_cell(c2)}</td>'
            f'<td class="ov-center">{fmt_cell(c3)}</td>'
            f'<td class="ov-left">{fmt_cell(c4)}</td>'
            f'<td class="ov-num ov-p">{fmt_cell(c5, dash_when_empty=True)}</td>'
            f'<td class="ov-num ov-p-rem">{fmt_cell(c6, dash_when_empty=True)}</td>'
            f'<td class="ov-num ov-s">{fmt_cell(c7, dash_when_empty=True)}</td>'
            f'<td class="ov-num ov-s-rem">{fmt_cell(c8, dash_when_empty=True)}</td>'
            f'<td class="ov-num ov-sl">{fmt_cell(c9, dash_when_empty=True)}</td>'
            f'<td class="ov-num ov-sl-rem">{fmt_cell(c10, dash_when_empty=True)}</td>'
            "</tr>"
        )

    overview_html = textwrap.dedent(f"""
    <style>
    .ov-wrap {{
      width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      margin-top: 6px;
      margin-bottom: 12px;
      border: 1.5px solid #1f2328;
      border-radius: 6px;
      background: #ffffff;
    }}
    table.ov-table {{
      border-collapse: collapse;
      table-layout: fixed;
      width: 100%;
      min-width: 640px;
      font-family: "Khmer OS Battambang", "Noto Sans Khmer", Arial, sans-serif;
      font-size: 11px;
      background: #ffffff;
      word-break: normal;
      overflow-wrap: break-word;
    }}
    table.ov-table th, table.ov-table td {{
      border: 1px solid #4b5563;
      padding: 3px 3px;
      vertical-align: middle;
      line-height: 1.35;
    }}
    .ov-col-no {{ width: 4%; }}
    .ov-col-lr {{ width: 4%; }}
    .ov-col-name {{ width: 14%; }}
    .ov-col-gen {{ width: 5%; }}
    .ov-col-role {{ width: 25%; }}
    .ov-col-num {{ width: 8%; }}

    .ov-th-gray {{
      background-color: #d9d9d9 !important;
      color: #000000 !important;
      font-weight: 700;
      text-align: center;
    }}
    .ov-th-p {{
      background-color: #009944 !important;
      color: #000000 !important;
      font-weight: 700;
      text-align: center;
    }}
    .ov-th-s {{
      background-color: #ffcc00 !important;
      color: #000000 !important;
      font-weight: 700;
      text-align: center;
    }}
    .ov-th-sl {{
      background-color: #e67300 !important;
      color: #000000 !important;
      font-weight: 700;
      text-align: center;
    }}
    .ov-th-sub-p {{
      background-color: #16a34a !important;
      color: #ffffff !important;
      font-weight: 700;
      text-align: center;
      font-size: 10px;
    }}
    .ov-th-sub-s {{
      background-color: #eab308 !important;
      color: #000000 !important;
      font-weight: 700;
      text-align: center;
      font-size: 10px;
    }}
    .ov-th-sub-sl {{
      background-color: #ea580c !important;
      color: #ffffff !important;
      font-weight: 700;
      text-align: center;
      font-size: 10px;
    }}
    tr.ov-section-row td.ov-sec-title {{
      background-color: #e5e7eb !important;
      color: #111827 !important;
      font-weight: 700;
      text-align: left;
      padding: 4px 6px;
      font-size: 11px;
    }}
    td.ov-center {{
      text-align: center;
      color: #111111;
      background-color: #ffffff;
    }}
    td.ov-left {{
      text-align: left;
      color: #111111;
      background-color: #ffffff;
    }}
    td.ov-bold {{
      font-weight: 700;
    }}
    td.ov-num {{
      text-align: center;
      font-weight: 600;
    }}
    td.ov-p {{ background-color: #16a34a !important; color: #ffffff !important; }}
    td.ov-p-rem {{ background-color: #15803d !important; color: #ffffff !important; }}
    td.ov-s {{ background-color: #facc15 !important; color: #111827 !important; }}
    td.ov-s-rem {{ background-color: #eab308 !important; color: #111827 !important; }}
    td.ov-sl {{ background-color: #f97316 !important; color: #ffffff !important; }}
    td.ov-sl-rem {{ background-color: #ea580c !important; color: #ffffff !important; }}

    @media (max-width: 640px) {{
      table.ov-table {{
        min-width: 580px;
        font-size: 9.5px;
      }}
      table.ov-table th, table.ov-table td {{
        padding: 2.5px 2px;
        line-height: 1.25;
      }}
    }}
    </style>
    <div class="ov-wrap">
    <table class="ov-table">
    <colgroup>
      <col class="ov-col-no">
      <col class="ov-col-lr">
      <col class="ov-col-name">
      <col class="ov-col-gen">
      <col class="ov-col-role">
      <col class="ov-col-num">
      <col class="ov-col-num">
      <col class="ov-col-num">
      <col class="ov-col-num">
      <col class="ov-col-num">
      <col class="ov-col-num">
    </colgroup>
    <thead>
    <tr>
      <th class="ov-th-gray" rowspan="2">ល.ស</th>
      <th class="ov-th-gray" rowspan="2">ល.រ</th>
      <th class="ov-th-gray" rowspan="2">គោត្តនាម-នាម</th>
      <th class="ov-th-gray" rowspan="2">ភេទ</th>
      <th class="ov-th-gray" rowspan="2">ឋានៈ</th>
      <th class="ov-th-p" colspan="2">P</th>
      <th class="ov-th-s" colspan="2">S</th>
      <th class="ov-th-sl" colspan="2">SL</th>
    </tr>
    <tr>
      <th class="ov-th-sub-p">បានប្រើ</th>
      <th class="ov-th-sub-p">នៅសល់</th>
      <th class="ov-th-sub-s">បានប្រើ</th>
      <th class="ov-th-sub-s">នៅសល់</th>
      <th class="ov-th-sub-sl">បានប្រើ</th>
      <th class="ov-th-sub-sl">នៅសល់</th>
    </tr>
    </thead>
    <tbody>
    {"".join(rows_html)}
    </tbody>
    </table>
    </div>
    """).strip()

    st.markdown(overview_html, unsafe_allow_html=True)


# --- បង្រួមទទឹង Selectbox (Searchbox) ឱ្យខ្លីស្អាត តែមិនដាច់ឈ្មោះ ---
st.markdown(
    """
    <style>
    div[data-testid="stSelectbox"] {
      max-width: 340px;
      width: 100%;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
      min-height: 38px;
    }
    div[data-testid="stSelectbox"] span {
      white-space: nowrap;
      overflow: visible;
      text-overflow: clip;
    }
    @media (max-width: 640px) {
      div[data-testid="stSelectbox"] {
        max-width: 260px;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- ផ្នែកបង្ហាញទិន្នន័យសំខាន់ (Main UI) ---
summary_df, load_err = load_csv_cached(csv_url)

if load_err:
    err_msg = (
        "មិនអាចទាញទិន្នន័យពី Google Sheet បានទេ។ សូមពិនិត្យមើលថា Google Sheet "
        "បានកំណត់ Share ជា **Anyone with the link (Viewer)** ឬនៅ។\n\n"
        f"ព័ត៌មានលម្អិត៖ `{load_err}`"
    )
    st.error(err_msg)
elif summary_df.empty:
    st.warning("Sheet សង្ខេបទទេ (គ្មានទិន្នន័យ)។")
else:
    detected_rem_cols = detect_remaining_columns(summary_df)
    name_col_idx = 2 if summary_df.shape[1] > 2 else 0
    raw_names = [
        normalize_name(v)
        for v in summary_df.iloc[:, name_col_idx].dropna().tolist()
        if normalize_name(v) != ""
    ]
    emp_names = list(dict.fromkeys(raw_names))

    if not emp_names:
        st.info("រកមិនឃើញបញ្ជីឈ្មោះបុគ្គលិកក្នុងជួរឈរទី ៣ ទេ — កំពុងបង្ហាញតារាងដើម៖")
        st.dataframe(summary_df, use_container_width=True)
    else:
        selected_emp = st.selectbox("ជ្រើសរើសឈ្មោះបុគ្គលិក", emp_names)

        matched_rows = summary_df[
            summary_df.iloc[:, name_col_idx].fillna("").map(normalize_name)
            == selected_emp
        ]

        # បង្ហាញ Card សង្ខេបភ្លាមៗដោយមិនជាប់សោ
        if not matched_rows.empty:
            render_employee_leave_card(matched_rows.iloc[0], detected_rem_cols)

        # ចាក់សោចាប់ពីតារាងប្រចាំខែចុះក្រោមរហូតដល់ Login ជោគជ័យ
        if render_login_lock_box():
            monthly_records, totals, debug_rows = compute_monthly_totals(
                selected_emp, MONTH_SHEETS, SPREADSHEET_ID
            )

            render_monthly_breakdown_table(monthly_records, totals, debug_rows)

            with st.expander("មើលទិន្នន័យ Sheet សង្ខេបទាំងមូល"):
                render_summary_overview_table(summary_df)
