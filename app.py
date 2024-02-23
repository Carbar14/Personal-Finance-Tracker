from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
import sqlite3
from helpers import login_required, get_db_connection
from datetime import timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date

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

    passwordHasher = PasswordHasher()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username:
            flash('Username is required!')
            conn.commit()
            conn.close()
            return render_template("login.html")
        elif not password:
            flash('Password is required!')
            conn.commit()
            conn.close()
            return render_template("login.html")
        elif not conn.execute("SELECT * FROM users WHERE username= ?", username).fetchall():
            flash("Username does not exist!")
            conn.commit()
            conn.close()
            return render_template("login.html")
        #hash
        
        hash = conn.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchall()[0]["hash"]
        ph = PasswordHasher()
        try:
            passwordMatches = ph.verify(hash, password)
        except VerifyMismatchError:
            passwordMatches = False
        if ph.check_needs_rehash(hash):
            conn.execute("INSERT INTO users (hash) VALUES (?) WHERE username = ?", (ph.hash(password), username))
        if not passwordMatches:
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
    conn.commit()
    conn.close()
    return render_template("login.html")

    

@app.route("/register", methods=["GET", "POST"])
def register():
    #establish connection to data base
    conn = get_db_connection()

    if request.method == "POST":
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
            #hash
            passwordHasher = PasswordHasher()
            hash = passwordHasher.hash(password)
            #registers user
            conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
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
    
    categoryFilter = None
    purchaseLocationFilter = None
    keywordsFilter = None
    dateFilter = None
    fromDateFilter =None
    toDateFilter = None
    fromPriceFilter = None
    toPriceFilter = None

    exps = conn.execute("SELECT * FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    total = conn.execute("SELECT SUM(price) AS sum FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()[0]["sum"]
    if request.method == "POST":
        
        
        # get filter selections
        categoryFilter = request.form.get("category")
        purchaseLocationFilter = request.form.get("purchaseLocation")
        keywordsFilter = request.form.get("keywords")
        dateFilter = request.form.get("date")
        fromDateFilter = request.form.get("fromDate")
        toDateFilter = request.form.get("toDate")
        fromPriceFilter = request.form.get("fromPrice")
        toPriceFilter = request.form.get("toPrice")

        if dateFilter and (fromDateFilter or toDateFilter):
            flash("Cannot do from-to date at the same time as a specific date")
        
        if (fromPriceFilter and toPriceFilter) and float(fromPriceFilter) > float(toPriceFilter):
            flash("From-price must be smaller than to-price")


        if fromDateFilter:
            fD = date.fromisoformat(fromDateFilter)
        if toDateFilter:
            tD = date.fromisoformat(toDateFilter)
        
        if  fromDateFilter and toDateFilter and (not dateIsLessThan(fD, tD)):
            flash("From-date must be less than to-date")

        floatedFromPriceFilter = 0
        if fromPriceFilter:
            floatedFromPriceFilter = float(fromPriceFilter)
        
        floatedToPriceFilter = 0
        if toPriceFilter:
            floatedToPriceFilter = float(toPriceFilter)
        
        
        exps = conn.execute("SELECT * FROM expenses WHERE"\
                            " user_id = ?"\
                            " AND CASE WHEN ? != '' THEN category = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN purchaseLocation = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN date = ? ELSE 1 END"\
                             " AND CASE WHEN ? != '' AND ? != '' THEN date BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN ? AND '9999-00-00'"\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN 0000-00-00  AND ?"\
                                " ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN price BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN price BETWEEN ? AND 99999999"\
                                " WHEN ? != '' AND ? == '' THEN price BETWEEN 0 AND ?"\
                                " ELSE 1 END"
                                #, fromPriceFilter, toPriceFilter, float(fromPriceFilter), float(toPriceFilter), fromPriceFilter, toPriceFilter, float(fromPriceFilter), fromPriceFilter, toPriceFilter, float(toPriceFilter)
                            , (session["user_id"], categoryFilter, categoryFilter, purchaseLocationFilter, purchaseLocationFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter , fromPriceFilter, toPriceFilter, floatedFromPriceFilter, floatedToPriceFilter, fromPriceFilter, toPriceFilter, floatedFromPriceFilter, fromPriceFilter, toPriceFilter, floatedToPriceFilter)).fetchall()
        total = conn.execute("SELECT SUM(price) AS sum FROM expenses WHERE"\
                            " user_id = ?"\
                            " AND CASE WHEN ? != '' THEN category = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN purchaseLocation = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN date = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN date BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN ? AND '9999-00-00'"\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN 0000-00-00  AND ?"\
                                " ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN price BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN price BETWEEN ? AND 99999999"\
                                " WHEN ? != '' AND ? == '' THEN price BETWEEN 0 AND ?"\
                                " ELSE 1 END"
                            , (session["user_id"], categoryFilter, categoryFilter, purchaseLocationFilter, purchaseLocationFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromPriceFilter, toPriceFilter, floatedFromPriceFilter, floatedToPriceFilter, fromPriceFilter, toPriceFilter, floatedFromPriceFilter, fromPriceFilter, toPriceFilter, floatedToPriceFilter)).fetchall()[0]["sum"]
    elif request.method == "GET":
        categoryFilter = categoryFilter if categoryFilter is not None else ""
        purchaseLocationFilter = purchaseLocationFilter if purchaseLocationFilter is not None else ""  
        keywordsFilter = keywordsFilter if keywordsFilter is not None else ""  
        dateFilter = dateFilter if dateFilter is not None else ""  
        fromDateFilter = fromDateFilter if fromDateFilter is not None else ""  
        toDateFilter = toDateFilter if toDateFilter is not None else ""  
        fromPriceFilter = fromPriceFilter if fromPriceFilter is not None else ""  
        toPriceFilter = toPriceFilter if toPriceFilter is not None else ""  

    return render_template("analyzeExpenses.html", categories=categories,purchaseLocations=purchaseLocations,expenses=exps,total=total,categoryFilter=categoryFilter,purchaseLocationFilter=purchaseLocationFilter,keywordsFilter=keywordsFilter,dateFilter=dateFilter,fromDateFilter=fromDateFilter,toDateFilter=toDateFilter,    fromPriceFilter=fromPriceFilter, toPriceFilter=toPriceFilter)

# checks if first date is less than second date
def dateIsLessThan(d1, d2):
    if d1.year > d2.year:
        return False
    elif d1.year == d2.year and d1.month > d2.month:
        return False
    elif d1.year == d2.year and d1.month == d2.month and d1.day > d2.day:
        return False
    return True


@app.route("/analyzeIncome", methods=["GET", "POST"])
@login_required
def analyzeIncome():
    conn = get_db_connection()
    categories = conn.execute("SELECT DISTINCT category FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    methods = conn.execute("SELECT DISTINCT method FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    
     
    categoryFilter = None
    methodFilter = None
    keywordsFilter = None
    dateFilter = None
    fromDateFilter =None
    toDateFilter = None
    fromIncomeFilter = None
    toIncomeFilter = None

    incs = conn.execute("SELECT * FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    total = conn.execute("SELECT SUM(income) AS sum FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()[0]["sum"]
    if request.method == "POST":
        

        # get filter selections
        categoryFilter = request.form.get("category")
        methodFilter = request.form.get("method")
        keywordsFilter = request.form.get("keywords")
        dateFilter = request.form.get("date")
        fromDateFilter = request.form.get("fromDate")
        toDateFilter = request.form.get("toDate")
        fromIncomeFilter = request.form.get("fromIncome")
        toIncomeFilter = request.form.get("toIncome")

        if dateFilter and (fromDateFilter or toDateFilter):
            flash("Cannot do from-to date at the same time as a specific date")
        
        if (fromIncomeFilter and toIncomeFilter) and float(fromIncomeFilter) > float(toIncomeFilter):
            flash("From-income must be smaller than to-income")


        if fromDateFilter:
            fD = date.fromisoformat(fromDateFilter)
        if toDateFilter:
            tD = date.fromisoformat(toDateFilter)
        
        if  fromDateFilter and toDateFilter and (not dateIsLessThan(fD, tD)):
            flash("From-date must be less than to-date")


        floatedFromIncomeFilter = 0
        if fromIncomeFilter:
            floatedFromIncomeFilter = float(fromIncomeFilter)
        
        floatedToIncomeFilter = 0
        if toIncomeFilter:
            floatedToIncomeFilter = float(toIncomeFilter)
        
        incs = conn.execute("SELECT * FROM incomes WHERE"\
                            " user_id = ?"\
                            " AND CASE WHEN ? != '' THEN category = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN method = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN date = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN date BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN ? AND '9999-00-00'"\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN 0000-00-00  AND ?"\
                                " ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN income BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN income BETWEEN ? AND 99999999"\
                                " WHEN ? != '' AND ? == '' THEN income BETWEEN 0 AND ?"\
                                " ELSE 1 END"
                            , (session["user_id"], categoryFilter, categoryFilter, methodFilter, methodFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromIncomeFilter, toIncomeFilter, floatedFromIncomeFilter, floatedToIncomeFilter, fromIncomeFilter, toIncomeFilter, floatedFromIncomeFilter, fromIncomeFilter, toIncomeFilter, floatedToIncomeFilter)).fetchall()
        total = conn.execute("SELECT SUM(income) AS sum FROM incomes WHERE"\
                            " user_id = ?"\
                            " AND CASE WHEN ? != '' THEN category = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN method = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN description LIKE ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' THEN date = ? ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN date BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN ? AND '9999-00-00'"\
                                " WHEN ? != '' AND ? == '' THEN date BETWEEN 0000-00-00  AND ?"\
                                " ELSE 1 END"\
                            " AND CASE WHEN ? != '' AND ? != '' THEN income BETWEEN ? AND ? "\
                                " WHEN ? != '' AND ? == '' THEN income BETWEEN ? AND 99999999"\
                                " WHEN ? != '' AND ? == '' THEN income BETWEEN 0 AND ?"\
                                " ELSE 1 END"
                            , (session["user_id"], categoryFilter, categoryFilter, methodFilter, methodFilter, keywordsFilter, f'%{keywordsFilter}%', dateFilter, dateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromDateFilter, toDateFilter, fromIncomeFilter, toIncomeFilter, floatedFromIncomeFilter, floatedToIncomeFilter, fromIncomeFilter, toIncomeFilter, floatedFromIncomeFilter, fromIncomeFilter, toIncomeFilter, floatedToIncomeFilter)).fetchall()[0]["sum"]
    elif request.method == "GET":
        categoryFilter = categoryFilter if categoryFilter is not None else ""
        methodFilter = methodFilter if methodFilter is not None else ""  
        keywordsFilter = keywordsFilter if keywordsFilter is not None else ""  
        dateFilter = dateFilter if dateFilter is not None else ""  
        fromDateFilter = fromDateFilter if fromDateFilter is not None else ""  
        toDateFilter = toDateFilter if toDateFilter is not None else ""  
        fromIncomeFilter = fromIncomeFilter if fromIncomeFilter is not None else ""  
        toIncomeFilter = toIncomeFilter if toIncomeFilter is not None else ""  

    return render_template("analyzeIncome.html", categories=categories, methods=methods, incomes=incs, total=total, categoryFilter=categoryFilter, methodFilter=methodFilter, keywordsFilter=keywordsFilter, dateFilter=dateFilter, fromDateFilter=fromDateFilter, toDateFilter=toDateFilter, fromIncomeFilter=fromIncomeFilter, toIncomeFilter=toIncomeFilter)



@app.route("/pieChart", methods=["GET", "POST"])
@login_required
def pieChart():
    conn = get_db_connection()
    exps = conn.execute("SELECT category, date, SUM(price * quantity) FROM expenses WHERE user_id = ? GROUP BY category", (session["user_id"],)).fetchall()
    incs = conn.execute("SELECT category, date, SUM(income) FROM incomes WHERE user_id = ? GROUP BY category", (session["user_id"],)).fetchall()

    expsFormatted = [{'category': category, 'price': price, 'date': date} for category, date, price in exps]
    incsFormatted = [{'category': category, 'income': income, 'date': date} for category, date, income in incs]

    return render_template("pieChart.html", incomes=incsFormatted, expenses=expsFormatted)


@app.route("/lineChart", methods=["GET", "POST"])
@login_required
def lineChart():
    conn = get_db_connection()
    exps = conn.execute("SELECT price, date FROM expenses WHERE user_id = ? ORDER BY date ASC", (session["user_id"],)).fetchall()
    incs = conn.execute("SELECT income, date FROM incomes WHERE user_id = ? ORDER BY date ASC", (session["user_id"],)).fetchall()

    expsFormatted = [{'price': price, 'date': date} for price, date in exps]
    incsFormatted = [{'income': income, 'date': date} for income, date in incs]

    return render_template("lineChart.html", incomes=incsFormatted, expenses=expsFormatted)