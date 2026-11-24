import pandas as pd
import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
month = st.selectbox("ជ្រើសរើសឈ្មោះ", ["ឡុង វណ្ណនី", "ឈន ធារ៉ា", "ហែម ណារ៉ា"])
try:
	df = pd.read_csv(csv_url)
	st.dataframe(df)
	import csv
    employees = {}
        for row in csv.DictReader(f):
            emp_id = row["id"].strip()
            employees[emp_id] = {
                "id": emp_id,
                "name": row["name"].strip(),
                "gender": row["gender"].strip(),
                "position": row["position"].strip(),
                "quotas": {
                    "P": int(row["annual_quota_p"]),
                    "S": int(row["short_quota_s"]),
                    "SL": int(row["sick_quota_sl"]),
                },
                "used": {"P": 0, "S": 0, "SL": 0},
                "nf": 0,
            }
    return employees


def apply_logs(employees: dict[str, dict], logs_path: Path) -> dict[str, dict]:
    with logs_path.open(mode="r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            emp_id = row["employee_id"].strip()
            ltype = row["leave_type"].strip()
            days = int(row["days"])
            nf = int(row.get("nf_count", 0) or 0)

            if emp_id in employees and ltype in employees[emp_id]["used"]:
                employees[emp_id]["used"][ltype] += days
                employees[emp_id]["nf"] += nf
    return employees


def get_employee_summary(emp: dict) -> dict:
    remaining = {
        k: emp["quotas"][k] - emp["used"][k]
        for k in ("P", "S", "SL")
    }
    return {
        "name": emp["name"],
        "gender": emp["gender"],
        "position": emp["position"],
        "used": emp["used"],
        "remaining": remaining,
        "nf": emp["nf"],
    }


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent
    emps = load_employees(base / "data" / "employees.csv")
    emps = apply_logs(emps, base / "data" / "leave_logs.csv")
    print(get_employee_summary(emps["1"]))
except Exception as e:
	st.error(f"មានបញ្ហាទាញទិន្នន័យ៖ {e}")
