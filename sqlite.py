import sqlite3
import random

# Create a new database file
conn = sqlite3.connect("university.db")
cursor = conn.cursor()

# =========================
# 1. Drop Old Tables if Exist
# =========================
cursor.executescript("""
DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Professors;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS Grades;
""")

# =========================
# 2. Create Tables
# =========================
cursor.executescript("""
CREATE TABLE Departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    building TEXT
);

CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

CREATE TABLE Professors (
    professor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    title TEXT,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    credits INTEGER,
    department_id INTEGER,
    professor_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id),
    FOREIGN KEY (professor_id) REFERENCES Professors(professor_id)
);

CREATE TABLE Enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    semester TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE Grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER,
    grade TEXT,
    FOREIGN KEY (enrollment_id) REFERENCES Enrollments(enrollment_id)
);
""")

# =========================
# 3. Insert Data
# =========================

# --- Departments ---
departments = [
    ("Computer Science", "Building A"),
    ("Software Engineering", "Building B"),
    ("Mathematics", "Building C"),
    ("Physics", "Building D"),
    ("English", "Building E"),
    ("Economics", "Building F"),
    ("Business Administration", "Building G"),
    ("Psychology", "Building H"),
    ("Political Science", "Building I"),
    ("Electrical Engineering", "Building J"),
]
cursor.executemany("INSERT INTO Departments (name, building) VALUES (?, ?)", departments)

# --- Pakistani Names ---
student_names = [
    "Ali Khan", "Ahmed Raza", "Hassan Ali", "Zain Abbas", "Bilal Ahmed",
    "Usman Tariq", "Ahsan Saeed", "Imran Butt", "Tahir Mahmood", "Kashif Iqbal",
    "Saad Malik", "Rizwan Javed", "Shahzad Akram", "Waseem Afzal", "Yasir Nawaz"
]

professor_names = [
    "Dr. Aslam", "Dr. Qureshi", "Dr. Farooq", "Dr. Salman", "Dr. Kamran",
    "Dr. Rafiq", "Dr. Nadeem", "Dr. Aftab", "Dr. Jamil", "Dr. Haroon"
]

# --- Professors (10 rows) ---
titles = ["Professor", "Associate Professor", "Assistant Professor"]
for i, prof in enumerate(professor_names):
    cursor.execute("""
        INSERT INTO Professors (name, title, department_id)
        VALUES (?, ?, ?)
    """, (prof, random.choice(titles), random.randint(1, 10)))

# --- Students (at least 15 rows) ---
for name in student_names:
    cursor.execute("""
        INSERT INTO Students (name, age, department_id)
        VALUES (?, ?, ?)
    """, (name, random.randint(18, 25), random.randint(1, 10)))

# --- Courses (at least 10 rows) ---
course_names = [
    "Data Structures", "Algorithms", "Operating Systems", "Database Systems", "Artificial Intelligence",
    "Machine Learning", "Calculus I", "Linear Algebra", "Quantum Mechanics", "Business Communication",
    "Macroeconomics", "Microeconomics", "Psychology Basics", "Political Theory", "Electrical Circuits"
]

for cname in course_names:
    cursor.execute("""
        INSERT INTO Courses (course_name, credits, department_id, professor_id)
        VALUES (?, ?, ?, ?)
    """, (cname, random.randint(2, 5), random.randint(1, 10), random.randint(1, 10)))

# --- Enrollments (each student enrolled in 3 random courses) ---
student_ids = [row[0] for row in cursor.execute("SELECT student_id FROM Students").fetchall()]
course_ids = [row[0] for row in cursor.execute("SELECT course_id FROM Courses").fetchall()]

semesters = ["Fall 2025", "Spring 2025", "Summer 2025"]

for student_id in student_ids:
    for course_id in random.sample(course_ids, 3):
        cursor.execute("""
            INSERT INTO Enrollments (student_id, course_id, semester)
            VALUES (?, ?, ?)
        """, (student_id, course_id, random.choice(semesters)))

# --- Grades (each enrollment has a grade) ---
grade_letters = ["A", "B", "C", "D", "F"]
enrollment_ids = [row[0] for row in cursor.execute("SELECT enrollment_id FROM Enrollments").fetchall()]

for eid in enrollment_ids:
    cursor.execute("INSERT INTO Grades (enrollment_id, grade) VALUES (?, ?)", (eid, random.choice(grade_letters)))

# =========================
# 4. Commit & Close
# =========================
conn.commit()
conn.close()

print("Database 'university.db' created successfully with Pakistani names and at least 10 rows per table!")
