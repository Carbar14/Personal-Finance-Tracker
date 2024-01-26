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
    conn = get_db_connection()
    exps = conn.execute("SELECT * FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    inc = conn.execute("SELECT * FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    conn.close()
    return render_template("index.html", expenses=exps, incomes=inc)

@app.route("/login", methods=["GET", "POST"])
def login():
    #clear session
    session.clear()

    #establish connection to data base
    conn = get_db_connection()

    if request.method == "POST":
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
            session["user_id"] = int(conn.execute("SELECT * FROM users WHERE username = ?", username).fetchall()[0]["id"])
            
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

@app.route("/add-expense", methods=["GET", "POST"])
@login_required
def addExpense():
    conn = get_db_connection()

    if request.method == "POST":
        userId = session["user_id"]
        category = request.form.get("category")
        description = request.form.get("description")
        purchaseLocation = request.form.get("purchaseLocation")
        quantity = int(request.form.get("quantity"))
        price = float(request.form.get("price"))
        date = request.form.get("date")

        conn.execute("INSERT INTO expenses (user_id, category, description, purchaseLocation, quantity, price, date) VALUES (?, ?, ?, ?, ?, ?, ?)", (userId, category, description, purchaseLocation, quantity, price, date))
        conn.commit()
        conn.close()
        return redirect("/")
    else:
        return render_template("addExpense.html")

@app.route("/add-income", methods=["GET", "POST"])
@login_required
def addIncome():
     conn = get_db_connection()

     if request.method == "POST":
        userId = session["user_id"]
        category = request.form.get("category")
        description = request.form.get("description")
        method = request.form.get("method")
        income = float(request.form.get("income"))
        date = request.form.get("date")

        conn.execute("INSERT INTO incomes (user_id, category, description, method, income, date) VALUES (?, ?, ?, ?, ?, ?)", (userId, category, description, method, income, date))
        conn.commit()
        conn.close()
        return redirect("/")
     else:
        return render_template("addIncome.html")
     

@app.route("/analyzeExpenses", methods=["GET", "POST"])
@login_required
def analyzeExpenses():
    conn = get_db_connection()
    categories = conn.execute("SELECT DISTINCT category FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    purchaseLocations = conn.execute("SELECT DISTINCT purchaseLocation FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    exps = conn.execute("SELECT * FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    total = conn.execute("SELECT SUM(price) AS sum FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()[0]["sum"]
    if request.method == "POST":
        

        # get filter selections
        categoryFilter = request.form.get("category")
        purchaseLocationFilter = request.form.get("purchaseLocation")
        keywordsFilter = request.form.get("keywords")
        dateFilter = request.form.get("date")
        
        exps = conn.execute("SELECT * FROM expenses WHERE user_id = ? AND CASE WHEN ? != '' THEN category = ? ELSE 1 END AND CASE WHEN ? != '' THEN purchaseLocation = ? ELSE 1 END AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END AND CASE WHEN ? != '' THEN date = ? ELSE 1 END" , (session["user_id"], categoryFilter, categoryFilter, purchaseLocationFilter, purchaseLocationFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter)).fetchall()
        total = conn.execute("SELECT SUM(income) AS sum FROM expenses WHERE user_id = ? AND CASE WHEN ? != '' THEN category = ? ELSE 1 END AND CASE WHEN ? != '' THEN purchaseLocation = ? ELSE 1 END AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END AND CASE WHEN ? != '' THEN date = ? ELSE 1 END" , (session["user_id"], categoryFilter, categoryFilter, purchaseLocationFilter, purchaseLocationFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter)).fetchall()
    return render_template("analyzeExpenses.html", categories=categories, purchaseLocations=purchaseLocations, expenses=exps, total=total)

@app.route("/analyzeIncome", methods=["GET", "POST"])
@login_required
def analyzeIncome():
    conn = get_db_connection()
    categories = conn.execute("SELECT DISTINCT category FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    methods = conn.execute("SELECT DISTINCT method FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    incs = conn.execute("SELECT * FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    total = conn.execute("SELECT SUM(income) AS sum FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()[0]["sum"]
    if request.method == "POST":
        

        # get filter selections
        categoryFilter = request.form.get("category")
        methodFilter = request.form.get("method")
        keywordsFilter = request.form.get("keywords")
        dateFilter = request.form.get("date")
        
        incs = conn.execute("SELECT * FROM incomes WHERE user_id = ? AND CASE WHEN ? != '' THEN category = ? ELSE 1 END AND CASE WHEN ? != '' THEN method = ? ELSE 1 END AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END AND CASE WHEN ? != '' THEN date = ? ELSE 1 END" , (session["user_id"], categoryFilter, categoryFilter, methodFilter, methodFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter)).fetchall()
        total = conn.execute("SELECT SUM(income) AS sum FROM incomes WHERE user_id = ? AND CASE WHEN ? != '' THEN category = ? ELSE 1 END AND CASE WHEN ? != '' THEN method = ? ELSE 1 END AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END AND CASE WHEN ? != '' THEN date = ? ELSE 1 END" , (session["user_id"], categoryFilter, categoryFilter, methodFilter, methodFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter)).fetchall()[0]["sum"]
    return render_template("analyzeIncome.html", categories=categories, methods=methods, incomes=incs, total=total)