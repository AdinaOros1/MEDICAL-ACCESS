import sqlite3
import math


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


def make_reservation(user_id, clinic_id, medical_service, date):
    reservation_id = db_insert(
        "INSERT INTO reservation (user_id, clinic_id, medical_service, date) VALUES (:user_id, :clinic_id, :medical_service, :date)",
        reservation,
    )

    return reservation_id

def add_medical_service(session_id, medical_service, capacity):
    clinic = db_fetch('SELECT * FROM clinic WHERE clinic_id = ?', (session_id,))
    if clinic:
        medical_service_id = db_insert(
            'INSERT INTO medical_service (clinic_id, service_name, capacity) VALUES (:clinic_id, :service_name, :capacity)',
            {'clinic_id': session_id, 'service_name': medical_service, 'capacity': capacity}
        )
        return medical_service_id  
    else:
        return None