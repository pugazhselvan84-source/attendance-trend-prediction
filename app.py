import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from database import load_records, save_record, get_storage_mode

st.set_page_config(page_title="Attendance Trend Prediction", page_icon="📊", layout="wide")

st.title("📊 Real-Time Student Attendance Trend Prediction System")
st.caption("Python • Pandas • Scikit-learn • MySQL • Streamlit")

REQUIRED_COLS = ["student_id", "student_name", "week", "classes_attended", "total_classes", "attendance_percentage"]

def clean_data(df):
    df = df.copy()
    for col in ["student_id", "student_name"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()
    for col in ["week", "classes_attended", "total_classes"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["week", "classes_attended", "total_classes"])
    df = df[(df["week"] >= 1) & (df["total_classes"] > 0)]
    df = df[(df["classes_attended"] >= 0) & (df["classes_attended"] <= df["total_classes"])]
    df["week"] = df["week"].astype(int)
    df["classes_attended"] = df["classes_attended"].astype(int)
    df["total_classes"] = df["total_classes"].astype(int)
    df["attendance_percentage"] = (df["classes_attended"] / df["total_classes"] * 100).round(2)
    return df[REQUIRED_COLS].sort_values(["student_id", "week"])

def predict_next_week(student_df):
    student_df = student_df.sort_values("week")
    if len(student_df) == 1:
        return float(student_df["attendance_percentage"].iloc[-1]), "Only one record is available; latest attendance is used as a simple estimate."
    model = LinearRegression()
    X = student_df[["week"]]
    y = student_df["attendance_percentage"]
    model.fit(X, y)
    next_week = int(student_df["week"].max()) + 1
    prediction = float(model.predict(pd.DataFrame({"week": [next_week]}))[0])
    prediction = max(0.0, min(100.0, prediction))
    return prediction, "Linear Regression trained on this student's weekly attendance history."

try:
    raw = load_records()
except Exception as e:
    st.error("Could not load records. Check your database settings or sample CSV.")
    st.exception(e)
    st.stop()

if "records" not in st.session_state:
    st.session_state.records = clean_data(raw)

with st.sidebar:
    st.header("Add Attendance Record")
    st.caption("Enter weekly totals. Example: attended 4 out of 5 classes.")
    with st.form("attendance_form", clear_on_submit=True):
        student_id = st.text_input("Student ID", placeholder="S101")
        student_name = st.text_input("Student Name", placeholder="Student name")
        week = st.number_input("Week number", min_value=1, max_value=52, value=1, step=1)
        total_classes = st.number_input("Total classes", min_value=1, max_value=20, value=5, step=1)
        classes_attended = st.number_input("Classes attended", min_value=0, max_value=20, value=4, step=1)
        submitted = st.form_submit_button("Save attendance")
        if submitted:
            if not student_id.strip() or not student_name.strip():
                st.error("Please enter both Student ID and Student Name.")
            elif classes_attended > total_classes:
                st.error("Classes attended cannot be greater than total classes.")
            else:
                row = {
                    "student_id": student_id.strip(),
                    "student_name": student_name.strip(),
                    "week": int(week),
                    "classes_attended": int(classes_attended),
                    "total_classes": int(total_classes),
                    "attendance_percentage": round(classes_attended / total_classes * 100, 2)
                }
                try:
                    save_record(row)
                    fresh = clean_data(load_records())
                    st.session_state.records = fresh
                    st.success("Attendance record saved.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save record: {e}")

st.info(f"Storage mode: **{get_storage_mode()}**. Predictions are estimates based on the available records, not guaranteed outcomes.")

df = clean_data(st.session_state.records)
if df.empty:
    st.warning("No attendance records found. Add a record or check the sample CSV.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Students", int(df["student_id"].nunique()))
col2.metric("Attendance records", int(len(df)))
col3.metric("Average attendance", f"{df['attendance_percentage'].mean():.1f}%")

st.subheader("Attendance Records")
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Predict a Student's Next-Week Attendance")
student_options = sorted(df["student_id"].unique().tolist())
selected_id = st.selectbox("Select Student ID", student_options)
student_df = df[df["student_id"] == selected_id].sort_values("week")
student_name = student_df["student_name"].iloc[-1]
prediction, note = predict_next_week(student_df)
latest = float(student_df["attendance_percentage"].iloc[-1])
required = st.number_input("Required attendance threshold (%)", min_value=1, max_value=100, value=75, step=1)
risk = "At Risk" if prediction < required else "On Track"

p1, p2, p3 = st.columns(3)
p1.metric("Latest attendance", f"{latest:.1f}%")
p2.metric("Predicted next week", f"{prediction:.1f}%")
p3.metric("Risk status", risk)

st.caption(note)

fig, ax = plt.subplots()
ax.plot(student_df["week"], student_df["attendance_percentage"], marker="o", label="Recorded attendance")
ax.scatter([int(student_df["week"].max()) + 1], [prediction], marker="x", s=100, label="Predicted next week")
ax.axhline(required, linestyle="--", label=f"Required threshold ({required}%)")
ax.set_xlabel("Week")
ax.set_ylabel("Attendance (%)")
ax.set_ylim(0, 105)
ax.set_title(f"Weekly Attendance Trend — {student_name} ({selected_id})")
ax.legend()
ax.grid(True, alpha=0.25)
st.pyplot(fig)
plt.close(fig)

st.subheader("Students Who May Need Support")
summary_rows = []
for sid, group in df.groupby("student_id"):
    group = group.sort_values("week")
    pred, _ = predict_next_week(group)
    summary_rows.append({
        "Student ID": sid,
        "Student Name": group["student_name"].iloc[-1],
        "Latest Attendance (%)": round(float(group["attendance_percentage"].iloc[-1]), 2),
        "Predicted Next Week (%)": round(pred, 2),
        "Status": "At Risk" if pred < required else "On Track"
    })
summary = pd.DataFrame(summary_rows).sort_values("Predicted Next Week (%)")
st.dataframe(summary, use_container_width=True, hide_index=True)

csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button("Download attendance records as CSV", data=csv_bytes, file_name="attendance_records.csv", mime="text/csv")

st.markdown("---")
st.caption("Academic demonstration project. Use real, verified institutional data before making student-related decisions.")
