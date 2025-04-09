from flask import Flask, session, Response, request, redirect, url_for, render_template
import db_utility_model as model
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

global user_data
username = "testuser"
password = "hello123"
password_hash = generate_password_hash(password)
user_data = {"User": {"views": 0, "password_hash": password_hash}}


app = Flask(__name__)


app.secret_key = b"ec68a703c4a06b435b5654c34da1d8c6ae35ffcf060c7d70a6ab4f9cec2f2025"



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ("username" in session):
            return Response("Acces Denied, you have to login", status=401)
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.get("/login")
def login_form():
    return render_template("login.html")


@app.post("/login")
def verify_login():
    username = request.form['username']
    password = request.form['password']
    error = None
    if username not in user_data:
        error = "Incorrect username"
        return Response(error)
      
    else:
        password_hash = user_data[username]["password_hash"]
        if not (check_password_hash(password_hash, password)):
            error = "Incorrect password"
            return Response(error)
    if error is None:
        session.clear()
        session["username"] = username
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login_form"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_form"))



@app.get("/")
def home():
    if "username" in session:
        username = session["username"]
        user_data[username]["views"] = user_data[username]["views"] + 1
        return render_template(
            "index.html",
            logged_in=True,
            username=username,
            views=user_data[username]["views"],
        )
    else:
        return render_template("index.html", logged_in=False, username=None, views=None)


@app.get("/sign_up")
def new_user_form():
    return render_template("sign_up.html")


@app.post("/sign_up")
def add_new_user():
    username = request.form.get("username")
    password = request.form.get("password")
    error = None
    if not(username):
        error = "Please enter a username"
    elif not(password):
        error = "Please enter a password"
    elif username in user_data:
        error = "This username already exists"
    if error is None:
        password_hash = generate_password_hash(password)
        user_data[username] = {'views': 0, 'password_hash': password_hash}
        
        session.clear()
        session["username"]= username
        return redirect(url_for('home'))
    else:
        return render_template("sign_up.html", error=error) 
    
@app.route("/index_user")
def index_user():
    if "username" in session:
        username = session["username"]
        reservations = []  # Replace with real data if needed
        return render_template("index_user.html", logged_in=True, username=username, reservations=reservations)
    return render_template("index_user.html", logged_in=False)


#clinic routes

@app.route("/index_clinic")
def index_clinic():
    return render_template("index_clinic.html")


@app.get("/login_clinic")
def login_clinic_form():
    return render_template("login_clinic.html")


@app.post("/login_clinic")
def verify_login_clinic():
    username = request.form['username']
    password = request.form['password']
    error = None
    if username not in user_data:
        error = "Incorrect username"
        return Response(error)
      
    else:
        password_hash = user_data[username]["password_hash"]
        if not (check_password_hash(password_hash, password)):
            error = "Incorrect password"
            return Response(error)
    if error is None:
        session.clear()
        session["username"] = username
        return redirect(url_for("home"))
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
    username = request.form.get("username")
    password = request.form.get("password")
    error = None
    if not(username):
        error = "Please enter a username"
    elif not(password):
        error = "Please enter a password"
    elif username in user_data:
        error = "This username already exists"
    if error is None:
        password_hash = generate_password_hash(password)
        user_data[username] = {'views': 0, 'password_hash': password_hash}
        
        session.clear()
        session["username"]= username
        return redirect(url_for('home'))
    else:
        return render_template("sign_up_clinic.html", error=error) 








