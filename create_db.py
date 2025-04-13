import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DBFILENAME = "medical_access.sqlite"





def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()


def create_user_table():
    db_run(
        "CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, first_name TEXT, last_name TEXT, password_hash TEXT, gender TEXT CHECK(gender in ('Male', 'Female')), email TEXT, age INTEGER, phone_number INTEGER)"
    )


def db_init(db_name=DBFILENAME):

    db_run(
        "CREATE TABLE IF NOT EXISTS clinic (clinic_id INTEGER PRIMARY KEY AUTOINCREMENT, password_hash TEXT, clinic_username TEXT, clinic_name TEXT, location TEXT, type TEXT CHECK(type in('State', 'Private')))"
    )
    db_run(
        "CREATE TABLE IF NOT EXISTS medical_service (medical_service_id INTEGER PRIMARY KEY AUTOINCREMENT, clinic_id INTEGER, service_name TEXT, capacity INTEGER, FOREIGN KEY (clinic_id) REFERENCES clinic(clinic_id))"
    )
    db_run(
        "CREATE TABLE IF NOT EXISTS reservation (reservation_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, clinic_id INTEGER, medical_service_id INTEGER, reservation_date DATE, FOREIGN KEY (user_id) REFERENCES user(user_id), FOREIGN KEY (clinic_id) REFERENCES clinic(clinic_id), FOREIGN KEY (medical_service_id) REFERENCES medical_service(medical_service_id))"
    )

    create_user_table()
    try:
        add_test_user()
    except:
        pass



#db_init()
