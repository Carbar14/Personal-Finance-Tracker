from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
import sqlite3
from helpers import login_required, get_db_connection
from datetime import timedelta

app = Flask(__name__)

#secret key
app.config['SECRET_KEY'] = 'ebdmaoze,32'

#session setup
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)




@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    #clear session
    session.clear()

    #establish connection to data base
    conn = get_db_connection()

    if request.method == "POST":
        print("a")
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        elif not conn.execute("SELECT * FROM users WHERE username= ?", username).fetchall():
            flash("Username does not exist!")
        elif not conn.execute("SELECT * FROM users WHERE username = ? AND hash = ?", (username, password)):
            flash("Password incorrect for that username!")
        else:
            #session the user
            session["user_id"] = conn.execute("SELECT * FROM users WHERE username = ?", username).fetchall()[0]["id"]

            #Keep signed in
            if not bool(request.form.get("keepSignedIn")):
                 session.permanent = True
                 app.permanent_session_lifetime = timedelta(days=1)
            else:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=31)

            conn.commit()
            conn.close()
            return redirect("/")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    #establish connection to data base
    conn = get_db_connection()

    if request.method == "POST":
        print("a")
        username = request.form.get("username")
        password = request.form.get("password")
        passwordCheck = request.form.get("passwordCheck")

        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        elif not passwordCheck:
            flash('Password confirmation is required!')
        elif password != passwordCheck:
            flash('Passwords do not match!')
        elif conn.execute("SELECT * FROM users WHERE username = ?", username).fetchall():
            flash('Username already taken')
        else:
            #registers user
            conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password))
            #sets session
            session["user_id"] = conn.execute("SELECT * FROM users WHERE username = ?", username).fetchall()[0]["id"]
            
            #Keep signed in
            if not bool(request.form.get("keepSignedIn")):
                 session.permanent = True
                 app.permanent_session_lifetime = timedelta(days=1)
            else:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=31)
            conn.commit()
            conn.close()
            return redirect("/")
    return render_template("register.html")


