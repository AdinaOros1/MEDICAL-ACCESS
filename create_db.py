import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DBFILENAME = "medical_access.sqlite"


def login(username, password):
    with sqlite3.connect(DBFILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, password_hash FROM user WHERE username = ?", (username,)
        )
        user = cur.fetchone()

        if user is None:
            return -1

        user_id, password_hash = user

        if check_password_hash(password_hash, password):
            return user_id  # Login successful
        else:
            return -1


def sign_up(
    username, first_name, last_name, password_hash, gender, email, age, phone_number
):
    with sqlite3.connect(DBFILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user (username, first_name, last_name, password_hash, gender, email, age, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                username,
                first_name,
                last_name,
                password_hash,
                gender,
                email,
                age,
                phone_number,
            ),
        )
        conn.commit()

        user_id = cur.lastrowid
    return user_id


def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()


def create_user_table():
    db_run(
        "CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, first_name TEXT, last_name TEXT, password_hash TEXT, gender TEXT CHECK(gender in ('Male', 'Female')), email TEXT, age INTEGER, phone_number INTEGER)"
    )


def add_test_user():
    username = "testuser"
    password = "hello123"
    first_name = "Anca"
    last_name ="Simona"
    gender = "Female"
    email = "testuser@example.com"
    age = 47
    phone_number = 0741201351
    

    password_hash = generate_password_hash(password)
    db_run(
        "INSERT INTO user (username, first_name, last_name, password_hash, gender, email, age, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (username, first_name, last_name, password_hash, gender, email, age, phone_number),
    )


def load(db_name=DBFILENAME):
    db_run("DROP TABLE IF EXISTS user")
    db_run("DROP TABLE IF EXISTS clinic")
    db_run("DROP TABLE IF EXISTS medical_service")
    db_run("DROP TABLE IF EXISTS reservation")

    db_run(
        "CREATE TABLE clinic (clinic_id INTEGER PRIMARY KEY AUTOINCREMENT, password_hash TEXT, clinic_username TEXT, clinic_name TEXT, location TEXT, type TEXT CHECK(type in('State', 'Private')))"
    )
    db_run(
        "CREATE TABLE medical_service (medical_service_id INTEGER PRIMARY KEY AUTOINCREMENT, clinic_id INTEGER, service_name TEXT, capacity INTEGER, FOREIGN KEY (clinic_id) REFERENCES clinic(clinic_id))"
    )
    db_run(
        "CREATE TABLE reservation (reservation_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, clinic_id INTEGER, medical_service_id INTEGER,  FOREIGN KEY (user_id) REFERENCES user(user_id), FOREIGN KEY (clinic_id) REFERENCES clinic(clinic_id), FOREIGN KEY (medical_service_id) REFERENCES medical_service(medical_service_id), date DATE)"
    )

    create_user_table()
    add_test_user()


# load recipe data
load()
