# 🎓 School Management System

A small Python project to manage **students, teachers and grades**. It has two front-ends on top of the same JSON database:

- **`school_cli.py`**: menu-driven command-line app built with Object-Oriented Programming (OOP).
- **`app.py`**: a Streamlit web UI with a dashboard, search, charts and forms.

Built by **Ronak De**.

---

## Features

- Register students (name, age, email, roll number)
- Register teachers (name, age, email, subject, employee ID)
- Add or update a student's marks per subject
- View student and teacher details
- Email validation and duplicate checks (roll number, employee ID)
- Data saved automatically in `school_data.json`

**Streamlit UI extras:** dashboard with metrics and chart, top students, search, student profile, delete with confirmation, grade letters.

---

## Tech Stack

| Part | Tool |
|---|---|
| Language | Python 3.9+ |
| Web UI | Streamlit |
| Tables / charts | pandas |
| Storage | JSON file (`school_data.json`) |
| OOP | `abc` module (Abstract Base Classes) |

---

## Project Structure

```
school_app/
├── app.py                # Streamlit web UI
├── school_cli.py         # OOP command-line version (Person, Student, Teachers)
├── requirements.txt      # streamlit, pandas
├── school_data.json      # created automatically on first save
├── .streamlit/
│   └── config.toml       # theme colours
└── README.md
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Web UI
streamlit run app.py

# 3. Command-line version (OOP)
python school_cli.py
```

> **Note:** the web UI stores grades as `"grades": {"Math": 75.0}`. The CLI stores them as `"gardes": {"Math": [75.0]}`. The web UI converts the old format automatically when it loads, but the CLI cannot read the new one. Use one front-end per data file.

---

## How the OOP Is Used (`school_cli.py`)

### Class diagram

```
          +-----------------------------+
          |        Person (ABC)         |
          |-----------------------------|
          | get_roles()   <<abstract>>  |
          | register()    <<abstract>>  |
          | validate_email()  <<static>>|
          +--------------+--------------+
                         ^
            inherits     |     inherits
          +--------------+--------------+
          |                             |
 +--------+---------+        +----------+---------+
 |     Student      |        |      Teachers      |
 |------------------|        |--------------------|
 | get_roles()      |        | get_roles()        |
 | register()       |        | register()         |
 | show_details()   |        | show_details()     |
 | add_grade()      |        |                    |
 +------------------+        +--------------------+
```

### Concepts used

| OOP concept | Where it is used |
|---|---|
| **Class and object** | `Student`, `Teachers`, `Person` are classes. `stud = Student()` and `teach = Teachers()` are objects. |
| **Abstraction** | `Person` inherits from `ABC`. Its `get_roles()` and `register()` are `@abstractmethod`, so `Person` cannot be created directly. |
| **Inheritance** | `Student(Person)` and `Teachers(Person)` reuse the parent's `validate_email()`. |
| **Polymorphism** | `register()` and `get_roles()` have the same name in both children but behave differently. |
| **Static method** | `validate_email()` is a `@staticmethod`. It needs no object data, so it is called as `Person.validate_email(email)`. |
| **Encapsulation (partial)** | Each class owns its own behaviour: input, validation and saving live inside its methods. |

### 1. Abstraction: `Person` is a blueprint

```python
class Person(ABC):

    @abstractmethod
    def get_roles(self):
        pass

    @abstractmethod
    def register(self):
        pass

    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email
```

`Person` only says **what** every person must be able to do (`get_roles`, `register`). It does not say **how**. Trying `Person()` raises a `TypeError`.

### 2. Inheritance: children reuse the parent

```python
class Student(Person): ...
class Teachers(Person): ...
```

Both classes get `validate_email()` from `Person` for free. No duplicate code.

### 3. Polymorphism: same method, different behaviour

| Method | `Student` | `Teachers` |
|---|---|---|
| `get_roles()` | returns `"student"` | returns `"Teacher"` |
| `register()` | asks name, age, email, **roll number** | asks name, age, email, **subject, emp_id** |
| duplicate check | by `roll` | by `emp_id` |
| saved in | `data["students"]` | `data["teachers"]` |

Because both follow the `Person` contract, you can call `.register()` on either object and the correct version runs.

### 4. Static method: a helper that needs no object

```python
if not Person.validate_email(email):
    print("Invalid Email")
    return
```

### 5. Class-specific behaviour

`Student` adds methods that teachers do not need: `add_grade()` and a `show_details()` that prints grades.

---

## Data Flow

```
User input (CLI or Streamlit form)
        |
        v
Validate (email format, duplicate roll / emp_id)
        |
        v
Update in-memory dict  data = {"students": [], "teachers": []}
        |
        v
save()  -->  school_data.json
        |
        v
Load again on next run
```

---

## Data Format (`school_data.json`)

```json
{
    "students": [
        {
            "name": "Ananya Das",
            "age": 18,
            "email": "ananya@example.com",
            "roll": 7,
            "grades": { "Physics": 88.5, "Math": 92.0 }
        }
    ],
    "teachers": [
        {
            "name": "Mr Rao",
            "age": 30,
            "email": "rao@example.com",
            "subject": "Physics",
            "emp_id": 1
        }
    ]
}
```

---

## Streamlit UI Pages

| Page | What you can do |
|---|---|
| **Dashboard** | Totals, class average, average marks chart, top 5 students |
| **Students** | Register, search all students, open a profile, delete |
| **Teachers** | Register, search by name or subject, delete |
| **Grades** | Pick a student and subject, save marks, remove a subject |

**Grade letters** (based on average): O ≥ 90, E ≥ 80, A ≥ 70, B ≥ 60, C ≥ 50, D ≥ 40, otherwise F.

**Validation rules:** name required, valid email format, unique roll number, unique employee ID, marks between 0 and 100.

---

## Possible Improvements

- Move the shared `data` dict into a `Database` class so `Student` and `Teachers` do not depend on a global variable (better encapsulation)
- Use classes in `app.py` too, so the CLI and web UI share the same `Student` and `Teachers` code
- Store attributes in `__init__` (name, age, email) so each object represents one real person
- Replace JSON with SQLite
- Add login for teachers and edit/update for student details

---

## Author

**Ronak De**