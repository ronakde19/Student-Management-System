import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

DB = Path("school_data.json")

st.set_page_config(page_title="School Manager", page_icon="🎓", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2.5rem; max-width: 1100px;}
    h1 {font-weight: 800; letter-spacing: -0.02em;}
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border-left: 5px solid #2F6F5E;
        border-radius: 6px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricValue"] {font-weight: 800;}
    .stButton > button, .stFormSubmitButton > button {font-weight: 600; border-radius: 6px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- data layer
def load():
    data = {"students": [], "teachers": []}
    if DB.exists():
        text = DB.read_text().strip()
        if text:
            data = json.loads(text)
    data.setdefault("students", [])
    data.setdefault("teachers", [])

    # migrate old format: "gardes" -> "grades", [marks] -> marks
    for s in data["students"]:
        grades = s.pop("gardes", None)
        if grades is not None and "grades" not in s:
            s["grades"] = grades
        s.setdefault("grades", {})
        for subject, mark in list(s["grades"].items()):
            if isinstance(mark, list):
                s["grades"][subject] = mark[-1] if mark else 0
    return data


def save(data):
    DB.write_text(json.dumps(data, indent=4))


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def average(student):
    marks = list(student["grades"].values())
    return round(sum(marks) / len(marks), 1) if marks else None


def grade_letter(avg):
    if avg is None:
        return "-"
    for cutoff, letter in [(90, "O"), (80, "E"), (70, "A"), (60, "B"), (50, "C"), (40, "D")]:
        if avg >= cutoff:
            return letter
    return "F"


def page_title(title, caption):
    st.title(title)
    st.caption(caption)


data = load()
students, teachers = data["students"], data["teachers"]


# ---------------------------------------------------------------- pages
def dashboard():
    page_title("Dashboard", "A quick look at your school.")

    all_marks = [m for s in students for m in s["grades"].values()]
    class_avg = round(sum(all_marks) / len(all_marks), 1) if all_marks else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", len(students))
    c2.metric("Teachers", len(teachers))
    c3.metric("Subjects taught", len({t["subject"].strip().lower() for t in teachers}))
    c4.metric("Class average", class_avg)

    st.write("")
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.subheader("Average marks by student")
        rows = [{"Student": s["name"], "Average": average(s)} for s in students if average(s) is not None]
        if rows:
            st.bar_chart(pd.DataFrame(rows).set_index("Student"), color="#2F6F5E")
        else:
            st.info("No grades yet. Add marks on the Grades page to see the chart.")

    with right:
        st.subheader("Top students")
        ranked = sorted(
            [s for s in students if average(s) is not None], key=average, reverse=True
        )[:5]
        if ranked:
            for i, s in enumerate(ranked, 1):
                st.write(f"**{i}. {s['name']}**  ·  {average(s)}  ·  Grade {grade_letter(average(s))}")
        else:
            st.info("Rankings appear once students have grades.")


def students_page():
    page_title("Students", "Register students and look up their records.")
    tab_reg, tab_all, tab_profile = st.tabs(["Register student", "All students", "Student profile"])

    with tab_reg:
        with st.form("student_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name")
            email = c2.text_input("Email")
            age = c1.number_input("Age", min_value=3, max_value=100, value=18, step=1)
            roll = c2.number_input("Roll number", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("Register student", type="primary")

        if submitted:
            if not name.strip():
                st.error("Enter the student's name.")
            elif not valid_email(email):
                st.error("Enter a valid email, like name@example.com.")
            elif any(s["roll"] == roll for s in students):
                st.error(f"Roll number {roll} is already taken.")
            else:
                students.append(
                    {"name": name.strip(), "age": int(age), "email": email.strip(),
                     "roll": int(roll), "grades": {}}
                )
                save(data)
                st.success(f"Registered {name.strip()} (roll {roll}).")

    with tab_all:
        if not students:
            st.info("No students yet. Register one in the first tab.")
        else:
            query = st.text_input("Search by name or roll number", placeholder="e.g. Ananya or 12")
            rows = [
                {"Roll": s["roll"], "Name": s["name"], "Age": s["age"], "Email": s["email"],
                 "Subjects": len(s["grades"]), "Average": average(s), "Grade": grade_letter(average(s))}
                for s in students
                if query.lower() in s["name"].lower() or query == str(s["roll"]) or not query
            ]
            df = pd.DataFrame(rows)
            st.dataframe(df.sort_values("Roll") if not df.empty else df, hide_index=True)
            st.caption(f"{len(rows)} of {len(students)} students")

    with tab_profile:
        if not students:
            st.info("No students yet.")
            return
        options = {f"{s['roll']} · {s['name']}": s for s in sorted(students, key=lambda x: x["roll"])}
        student = options[st.selectbox("Choose a student", list(options))]

        avg = average(student)
        c1, c2, c3 = st.columns(3)
        c1.metric("Roll number", student["roll"])
        c2.metric("Average", avg if avg is not None else "-")
        c3.metric("Grade", grade_letter(avg))
        st.write(f"**Email:** {student['email']}  \n**Age:** {student['age']}")

        if student["grades"]:
            gdf = pd.DataFrame(
                {"Subject": list(student["grades"]), "Marks": list(student["grades"].values())}
            )
            g1, g2 = st.columns([2, 3], gap="large")
            g1.dataframe(gdf, hide_index=True)
            g2.bar_chart(gdf.set_index("Subject"), color="#2F6F5E")
        else:
            st.info("No grades recorded yet.")

        with st.expander("Danger zone"):
            confirm = st.checkbox(f"Yes, delete {student['name']}", key=f"del_{student['roll']}")
            if st.button("Delete student", disabled=not confirm):
                students.remove(student)
                save(data)
                st.rerun()


def teachers_page():
    page_title("Teachers", "Register teachers and see who teaches what.")
    tab_reg, tab_all = st.tabs(["Register teacher", "All teachers"])

    with tab_reg:
        with st.form("teacher_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name")
            email = c2.text_input("Email")
            age = c1.number_input("Age", min_value=18, max_value=100, value=30, step=1)
            emp_id = c2.number_input("Employee ID", min_value=1, value=1, step=1)
            subject = st.text_input("Subject")
            submitted = st.form_submit_button("Register teacher", type="primary")

        if submitted:
            if not name.strip() or not subject.strip():
                st.error("Enter the teacher's name and subject.")
            elif not valid_email(email):
                st.error("Enter a valid email, like name@example.com.")
            elif any(t["emp_id"] == emp_id for t in teachers):
                st.error(f"Employee ID {emp_id} is already taken.")
            else:
                teachers.append(
                    {"name": name.strip(), "age": int(age), "email": email.strip(),
                     "subject": subject.strip(), "emp_id": int(emp_id)}
                )
                save(data)
                st.success(f"Registered {name.strip()} ({subject.strip()}).")

    with tab_all:
        if not teachers:
            st.info("No teachers yet. Register one in the first tab.")
            return
        query = st.text_input("Search by name or subject", placeholder="e.g. Physics")
        rows = [
            {"Emp ID": t["emp_id"], "Name": t["name"], "Subject": t["subject"],
             "Age": t["age"], "Email": t["email"]}
            for t in teachers
            if query.lower() in t["name"].lower() or query.lower() in t["subject"].lower()
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True)

        with st.expander("Danger zone"):
            options = {f"{t['emp_id']} · {t['name']}": t for t in teachers}
            chosen = options[st.selectbox("Choose a teacher to delete", list(options))]
            confirm = st.checkbox(f"Yes, delete {chosen['name']}", key=f"delt_{chosen['emp_id']}")
            if st.button("Delete teacher", disabled=not confirm):
                teachers.remove(chosen)
                save(data)
                st.rerun()


def grades_page():
    page_title("Grades", "Add or update a student's marks for a subject.")
    if not students:
        st.info("Register a student first, then come back to add grades.")
        return

    options = {f"{s['roll']} · {s['name']}": s for s in sorted(students, key=lambda x: x["roll"])}
    student = options[st.selectbox("Student", list(options))]

    known = sorted({t["subject"] for t in teachers} | set(student["grades"]))
    other = "Other (type below)"
    with st.form("grade_form"):
        c1, c2 = st.columns(2)
        pick = c1.selectbox("Subject", known + [other])
        marks = c2.number_input("Marks (out of 100)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
        custom = st.text_input("New subject name", disabled=False, help="Only used when 'Other' is selected.")
        submitted = st.form_submit_button("Save marks", type="primary")

    if submitted:
        subject = custom.strip() if pick == other else pick
        if not subject:
            st.error("Enter a subject name.")
        else:
            updated = subject in student["grades"]
            student["grades"][subject] = marks
            save(data)
            st.success(f"{'Updated' if updated else 'Added'} {subject}: {marks} for {student['name']}.")

    st.subheader(f"{student['name']}'s marks")
    if student["grades"]:
        gdf = pd.DataFrame({"Subject": list(student["grades"]), "Marks": list(student["grades"].values())})
        st.dataframe(gdf, hide_index=True)
        remove = st.selectbox("Remove a subject", ["-"] + list(student["grades"]))
        if remove != "-" and st.button(f"Remove {remove}"):
            del student["grades"][remove]
            save(data)
            st.rerun()
    else:
        st.info("No marks yet for this student.")


# ---------------------------------------------------------------- navigation
PAGES = {
    "📊 Dashboard": dashboard,
    "🧑‍🎓 Students": students_page,
    "🧑‍🏫 Teachers": teachers_page,
    "📝 Grades": grades_page,
}

with st.sidebar:
    st.markdown("## 🎓 School Manager")
    choice = st.radio("Go to", list(PAGES), label_visibility="collapsed")
    st.divider()
    st.caption(f"{len(students)} students · {len(teachers)} teachers")

PAGES[choice]()