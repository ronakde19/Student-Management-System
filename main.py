import json
from abc import ABC, abstractmethod
from pathlib import Path

database = "school_data.json"
data = {"students": [], "teachers": []} # copy 

if Path(database).exists():
    with open(database, 'r') as f:
        content = f.read()
        if content:
            data = json.loads(content)

def save():
    with open(database,"w") as f:
        json.dump(data,f, indent=4)


class Person(ABC):

    @abstractmethod
    def get_roles():
        pass

    @abstractmethod
    def register(self):
        pass

    @staticmethod
    def validate_email(email):
        if "@" in email and "." in email:
            return True
        else:
            return False

class Student(Person):

    def get_roles(self):
        return "student"

    def register(self):
        name = input("Enter name ")
        age = int(input("Enter age "))
        email = input("Enter your mail ")
        roll = int(input("Enter roll number "))

        if not Person.validate_email(email):
            print("Invalid Email")
            return

        for i in data['students']:
            if i['roll'] == roll:
                print("Student already exist")
                return

        data['students'].append({
            "name" : name,
            "age" : age,
            "email" : email,
            "roll" : roll,
            "gardes" : {}
        })
        save()
        print(f"student {name} registered")

    def show_details(self):
        roll = int(input("Enter Roll: "))
        for s in data['students']:
            if s['roll'] == roll:
                gardes = s['gardes']

                print(f"\n  Name     : {s['name']}")
                print(f"  Roll no  : {s['roll']}")
                print(f"  Grades   : {gardes}")
                return 

    def add_grade(self):
        roll = int(input("Enter roll: "))
        subject = input("Enter Subject: ")
        marks = float(input("marks"))

        for i in data['students']:
            if i['roll'] == roll:
                i['gardes'][subject] = [marks]
                save()
                print("grades added successfully")
                return
            print("student not found")


class Teachers(Person):
    def get_roles(self):
        return "Teacher"

    def register(self):
        name = input("Enter name ")
        age = int(input("Enter age "))
        email = input("Enter your mail ")
        subject = input("Enter the subject")
        emp_id = int(input("Enter emp_id number "))

        if not Person.validate_email(email):
            print("Invalid Email")
            return

        for i in data['teachers']:
            if i['emp_id'] == emp_id:
                print("Employee already exist")
                return

        data['teachers'].append({
            "name" : name,
            "age" : age,
            "email" : email,
            "subject" : subject,
            "emp_id" : emp_id
        })
        save()
        print(f"Teacher {name} registered")

    def show_details(self):
        emp_id = int(input("Enter employee id"))
        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                print(f"\n  Name     : {t['name']}")
                print(f"  Subject  : {t['subject']}")
                print(f"  Emp ID   : {t['emp_id']}")
                return
        print("Teacher not found.")

 

stud = Student()
teach = Teachers()

print("press 1 to register as a student")
print("press 2 to register as a  teacher")
print("press 3 to add grades")
print("press 4 to show student detail")
print("press 5 to show teacher detail")

choice = int(input("Enter your choice "))

if choice == 1:
    stud.register()

elif choice == 2:
    teach.register()

elif choice == 3:
    stud.add_grade()

elif choice == 4:
    stud.show_details()

elif choice == 5:
    teach.show_details()


    
