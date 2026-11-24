import pandas as pd
import streamlit as st
st.title("វត្តមាន")
sheet_url = "https://docs.google.com/spreadsheets/d/1a_JSto3zLs_LGue6SfJyukmdPaw18XQ9eoWY4VeH_nE/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
month = st.selectbox("ជ្រើសរើសឈ្មោះ", ["ឡុង វណ្ណនី", "ឈន ធារ៉ា", "ហែម ណារ៉ា"])
try:
	df = pd.read_csv(csv_url)
	st.dataframe(df)
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
