from flask import Flask, session, Response, request, redirect, url_for, render_template
import db_utility_model as db_model
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import create_db


app = Flask(__name__)
create_db.db_init()


app.secret_key = b"ec68a703c4a06b435b5654c34da1d8c6ae35ffcf060c7d70a6ab4f9cec2f2025"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ("username" in session):
            return Response("Acces Denied, you have to login", status=401)
        else:
            return f(*args, **kwargs)

    return decorated_function


def login_required_clinic(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ("clinic_username" in session):
            return Response("Acces Denied, you have to login", status=401)
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.get("/login")
def login_form():
    return render_template("login.html")


@app.post("/login")
def verify_login():
    username = request.form["username"]
    password = request.form["password"]
    error = None
    user_id = db_model.login_user_db(username, password)
    if user_id == -1:
        error = "Incorrect username/password"
        return Response(error)

    if error is None:
        session.clear()
        session["username"] = username
        return redirect(url_for("index_user"))
    else:
        return redirect(url_for("login_form"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index_user"))


@app.get("/")
def home():
    if "username" in session:
        username = session["username"]
        return render_template(
            "index.html",
            logged_in=True,
            username=username,
        )

    elif "clinic_username" in session:
        clinic_username = session["clinic_username"]
        return render_template(
            "index.html",
            logged_in=True,
            username=clinic_username,
        )
    else:
        return render_template("index.html", logged_in=False, username=None, views=None)


@app.get("/sign_up")
def new_user_form():
    return render_template("sign_up.html")


@app.post("/sign_up")
def add_new_user():
    username = request.form.get("username")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    gender = request.form.get("gender")
    email = request.form.get("email")
    age = request.form.get("age")
    phone_number = request.form.get("phone_number")
    password = request.form.get("password")
    error = None
    if not (username):
        error = "Please enter a username"
    elif not (password):
        error = "Please enter a password"
    else:
        user_id = db_model.sign_up_user_db(
            username, first_name, last_name, password, gender, email, age, phone_number
        )
        if user_id == -1:
            error = "This username already exists in the database"
    if error is None:
        session.clear()
        session["username"] = username
        return redirect(url_for("verify_login"))
    else:
        return render_template("sign_up.html", error=error)


@app.route("/index_user")
def index_user():
    if "username" in session:
        username = session["username"]
        reservations =db_model.get_reservations(session)  
        print(reservations)
        return render_template(
            "index_user.html",
            logged_in=True,
            username=username,
            reservations=reservations,
        )
    return render_template("index_user.html", logged_in=False)


# clinic routes


@app.route("/index_clinic")
def index_clinic():
    if "clinic_username" in session:
        clinic_username = session["clinic_username"]
        return render_template(
            "index_clinic.html",
            logged_in=True,
            username=clinic_username,
        )
    return render_template("index_clinic.html")


@app.get("/login_clinic")
def login_clinic_form():
    return render_template("login_clinic.html")


@app.post("/login_clinic")
def verify_login_clinic():
    clinic_username = request.form["clinic_username"]
    password = request.form["password"]
    error = None
    clinic_id = db_model.login_clinic_db(clinic_username, password)
    if clinic_id == -1:
        error = "Fail incorrect username/password"
        return Response(error)
    if error is None:
        session.clear()
        session["clinic_username"] = clinic_username
        return redirect(url_for("index_clinic"))
    else:
        return redirect(url_for("login_clinic_form"))


@app.post("/logout_clinic")
def logout_clinic():
    session.clear()
    return redirect(url_for("index_clinic"))


@app.get("/sign_up_clinic")
def sign_up_form():
    return render_template("sign_up_clinic.html")


@app.post("/sign_up_clinic")
def sign_up_clinic():
    clinic_username = request.form.get("clinic_username")
    password = request.form.get("password")
    clinic_name = request.form.get("clinic_name")
    location = request.form.get("location")
    clinic_type = request.form.get("type")
    error = None
    if not (clinic_username):
        error = "Please enter a clinic username"
    elif not (password):
        error = "Please enter a password"
    else:
        clinic_id = db_model.sign_up_clinic_db(
            clinic_name, clinic_username, location, clinic_type, password
        )
        if clinic_id == -1:
            error = "This clinic username already exists in the database"
    if error is None:
        session.clear()
        session["clinic_username"] = clinic_username
        return redirect(url_for("verify_login_clinic"))
    else:
        return render_template("sign_up_clinic.html", error=error)


@app.get("/add_medical_service")
@login_required_clinic
def add_medical_service_form():
    return render_template("add_medical_service.html")


@app.post("/add_medical_service")
def add_medical_service():
    service_name = request.form.get("service_name")
    capacity = request.form.get("capacity")

    if not service_name or not capacity:
        return "All fields are required", 400

    try:
        capacity = int(capacity)
    except ValueError:
        return "Capacity must be a number", 400

    session_id = session

    result = db_model.add_medical_service_db(session_id, service_name, capacity)

    if result is None:
        return "Failed to add medical service", 500

    return redirect(url_for("index_clinic"))


@app.get("/make_reservation")
@login_required
def make_a_reservation_form():
    services_and_clinics = db_model.get_clinic_and_service_names_db()
    return render_template("make_reservation.html", medical_services=services_and_clinics)


@app.post("/make_reservation")
def make_a_reservation():
    service_and_clinic_id = request.form.get("service_id")
    reservation_date = request.form.get("reservation_date")

    if not service_and_clinic_id or not reservation_date:
        return "All fields are required", 400
    
    if not session or 'username' not in session:
        return "User not authenticated", 401
    
    splited = service_and_clinic_id.split("-")
    service_id=splited[0]
    clinic_id=splited[1]
    
    
    
    reservation_id = db_model.make_reservation_db(session, service_id, clinic_id, reservation_date)

    if reservation_id:
        return redirect(url_for("index_user"))
    else:
        return "Reservation failed", 500
    

    
