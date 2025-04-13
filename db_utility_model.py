import sqlite3
import math
from werkzeug.security import generate_password_hash, check_password_hash


DBFILENAME = "medical_access.sqlite"


# Utility functions
def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        # to allow access to columns by name in res
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        # convert to a python dictionary for convenience
        if all:
            res = cur.fetchall()
            if res:
                res = [dict(e) for e in res]
            else:
                res = []
        else:
            res = cur.fetchone()
            if res:
                res = dict(res)
    return res


def db_insert(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid


def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()


def db_update(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount


def read(reservation_id):
    found = db_fetch(
        "SELECT * FROM reservation WHERE reservation_id = ?", (reservation_id,)
    )
    if not (found is None):
        found["user"] = db_fetch(
            "SELECT username FROM user WHERE user_id = ?", (found["user_id"],)
        )
        found["clinic"] = db_fetch(
            "SELECT clinic_name FROM clinic WHERE clinic_id = ?", (found["clinic_id"],)
        )
        found["medical_service"] = db_fetch(
            "SELECT service_name FROM medical_service WHERE medical_service_id = ?",
            (found["medical_service_id"],),
        )

    return found


def login_user_db(username, password):
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
        
def login_clinic_db(clinic_username, password):
    with sqlite3.connect(DBFILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT clinic_id, password_hash FROM clinic WHERE clinic_username = ?", (clinic_username,)
        )
        clinic_row = cur.fetchone()

        if clinic_row is None:
            return -1

        #clinic_id, password_hash = clinic_row
        clinic_id=clinic_row[0]
        password_hash=clinic_row[1]

        if check_password_hash(password_hash, password):
            return clinic_id  # Login successful
        else:
            return -1


def sign_up_user_db(
    username, first_name, last_name, password_hash, gender, email, age, phone_number
):
    with sqlite3.connect(DBFILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM user WHERE username = ?", (username,)
        )
        existing_user = cur.fetchone()

        if existing_user:
            return -1 
        password_hash = generate_password_hash(password)
        
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

def sign_up_clinic_db(
    clinic_name, clinic_username, location, clinic_type, password
):
    if clinic_type not in ['State', 'Private']:
        raise ValueError("Invalid clinic type. Must be 'State' or 'Private'.")
    
    with sqlite3.connect(DBFILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT clinic_id FROM clinic WHERE clinic_username = ?", (clinic_username,)
        )
        existing_clinic_user = cur.fetchone()

        if existing_clinic_user:
            return -1 
        password_hash = generate_password_hash(password)
        
        cur.execute(
            "INSERT INTO clinic (clinic_username, clinic_name, location, type, password_hash) VALUES (?, ?, ?, ?, ?)",
            (
                clinic_username, 
                clinic_name, 
                location, 
                clinic_type,
                password_hash
            ),
        )
        conn.commit()

        clinic_id = cur.lastrowid
    return clinic_id


def make_reservation_db(session_id, clinic_id, medical_service_id, reservation_date):
    username = session_id['username']
    
    user_row = db_fetch('SELECT * FROM user WHERE username = ?', (username,))
    if user_row:
        user_id=user_row['user_id']
        reservation_id = db_insert('INSERT INTO reservation (user_id, clinic_id, medical_service_id, reservation_date) VALUES (:user_id, :clinic_id, :medical_service_id, :reservation_date)', {'user_id': user_id, 'clinic_id': clinic_id, 'medical_service_id': medical_service_id, 'reservation_date': reservation_date})
        return reservation_id
    else:
        return None

def add_medical_service_db(session_id, service_name, capacity):
    clinic_username = session_id['clinic_username']
    
    clinic_row= db_fetch('SELECT * FROM clinic WHERE clinic_username = ?', (clinic_username,))
    
    if clinic_row:
        clinic_id=clinic_row['clinic_id']
        medical_service_id = db_insert(
            'INSERT INTO medical_service (clinic_id, service_name, capacity) VALUES (:clinic_id, :service_name, :capacity)',
            {'clinic_id': clinic_id, 'service_name': service_name, 'capacity': capacity}
        )
        return medical_service_id  
    else:
        return None