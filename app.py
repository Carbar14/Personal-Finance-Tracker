from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
import sqlite3
from helpers import login_required, get_db_connection
from datetime import timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date, datetime

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
    #establish connection to data base
    conn = get_db_connection()

    #gets all expenses and incomes in variables
    exps = conn.execute("SELECT * FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    inc = conn.execute("SELECT * FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    print(exps[1]["color"])
    conn.close()
    return render_template("index.html", expenses=exps, incomes=inc)

@app.route("/login", methods=["GET", "POST"])
def login():
    #clear session
    session.clear()

    #establish connection to data base
    conn = get_db_connection()

    #Post
    if request.method == "POST":
        #gets username and password from login form
        username = request.form.get("username")
        password = request.form.get("password")
        
        #Username not inputted
        if not username:
            flash('Username is required!')
            conn.commit()
            conn.close()
            return render_template("login.html")
        #Password not inputted
        elif not password:
            flash('Password is required!')
            conn.commit()
            conn.close()
            return render_template("login.html")
        #Username doesn't exist in database
        elif not conn.execute("SELECT * FROM users WHERE username= ?", (username,)).fetchall():
            flash("Username does not exist!")
            conn.commit()
            conn.close()
            return render_template("login.html")
        
        #gets users password hash
        hash = conn.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchall()[0]["hash"]
        #establish password hasher
        ph = PasswordHasher()

        #sets password matches variable to true if it matches the hash. False if doesn't.
        try:
            passwordMatches = ph.verify(hash, password)
        except VerifyMismatchError:
            passwordMatches = False

        #Password rehash
        if ph.check_needs_rehash(hash):
            conn.execute("INSERT INTO users (hash) VALUES (?) WHERE username = ?", (ph.hash(password), username))
        #Password incorrect    
        if not passwordMatches:
            flash("Password incorrect for that username!")
        else:
            #session the user
            session["user_id"] = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()[0]["id"]

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
    #Post
    if request.method == "POST":
        #Get username, password, and password check from register form
        username = request.form.get("username")
        password = request.form.get("password")
        passwordCheck = request.form.get("passwordCheck")

        # Username not inputted
        if not username:
            flash('Username is required!')
        # Password not inputted
        elif not password:
            flash('Password is required!')
        # Password check not inputted
        elif not passwordCheck:
            flash('Password confirmation is required!')
        # Password and Password check don't match
        elif password != passwordCheck:
            flash('Passwords do not match!')
        # Username inputted doesn't exist
        elif conn.execute("SELECT * FROM users WHERE username = ?", username).fetchall():
            flash('Username already taken')
        #Everything checks out
        else:
            # establish password hasher
            passwordHasher = PasswordHasher()
            #hash password
            hash = passwordHasher.hash(password)

            #registers user
            conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
            #sets session
            session["user_id"] = int(conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()[0]["id"])
            
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
    #establish connection to data base
    conn = get_db_connection()

    if request.method == "POST":
        #gets data from form
        userId = session["user_id"]

        if request.form.get("categoryText"):
            category = request.form.get("categoryText")
        elif request.form.get("categorySelect"):
            category = request.form.get("categorySelect")
        else:
            category = ""
        description = request.form.get("description")
        purchaseLocation = request.form.get("purchaseLocation")
        quantity = int(request.form.get("quantity"))
        price = float(request.form.get("price"))
        date = request.form.get("date")
        color = request.form.get("color")

        #inserts into database
        conn.execute("INSERT INTO expenses (user_id, category, description, purchaseLocation, quantity, price, date, color) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (userId, category, description, purchaseLocation, quantity, price, date, color))

        conn.commit()
        conn.close()
        return redirect("/")
    else:
         #get all income categories
        categories = conn.execute("SELECT DISTINCT category FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
        conn.close()
        return render_template("addExpense.html", categories=categories)

@app.route("/add-income", methods=["GET", "POST"])
@login_required
def addIncome():
    #establish connection to data base
     conn = get_db_connection()

     if request.method == "POST":
        #gets data from form
        userId = session["user_id"]
        if request.form.get("categoryText"):
            category = request.form.get("categoryText")
        elif request.form.get("categorySelect"):
            category = request.form.get("categorySelect")
        else:
            category = ""
            
        description = request.form.get("description")
        method = request.form.get("method")
        income = float(request.form.get("income"))
        date = request.form.get("date")
        color = request.form.get("color")

        #inserts into database
        conn.execute("INSERT INTO incomes (user_id, category, description, method, income, date, color) VALUES (?, ?, ?, ?, ?, ?, ?)", (userId, category, description, method, income, date, color))

        conn.commit()
        conn.close()
        return redirect("/")
     else:
        #get all income categories
        categories = conn.execute("SELECT DISTINCT category FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()

        conn.close()
        return render_template("addIncome.html", categories=categories)
     


@app.route('/color-category', methods=['POST'])
def color_category():
    #establish connection to data base
    conn = get_db_connection()

    #get data from post
    category = request.form.get('category')
    color = request.form.get('color')
    type = request.form.get("type")

    print(type + "   " + category + "   " + color)

    conn.execute(f"UPDATE {type} SET color = ? WHERE category = ?", (color, category))
    conn.commit()
    conn.close()
    
    
    return 'Color category updated successfully', 200

@app.route('/delete', methods=['POST'])
def delete():
    #establish connection to database
    conn = get_db_connection()

    type = request.form.get("type")
    id = request.form.get("id")
    conn.execute(f"DELETE from {type} WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/analyzeExpenses", methods=["GET", "POST"])
@login_required
def analyzeExpenses():
    #establish connection to data base
    conn = get_db_connection()

    #gets distinct catagories and purshase locations
    categories = conn.execute("SELECT DISTINCT category FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    purchaseLocations = conn.execute("SELECT DISTINCT purchaseLocation FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    #sets filters to nothing off the start
    categoryFilter = None
    purchaseLocationFilter = None
    keywordsFilter = None
    dateFilter = None
    fromDateFilter =None
    toDateFilter = None
    fromPriceFilter = None
    toPriceFilter = None

    #gets all expenses
    exps = conn.execute("SELECT * FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    #gets sum of all expenses
    total = conn.execute("SELECT SUM(price) AS sum FROM expenses WHERE user_id = ?", (session["user_id"],)).fetchall()[0]["sum"]

    #post
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

        #checks for if from-to and singular date is on at the same time
        if dateFilter and (fromDateFilter or toDateFilter):
            flash("Cannot do from-to date at the same time as a specific date")
        
        #checks if price filters are valid
        if (fromPriceFilter and toPriceFilter) and float(fromPriceFilter) > float(toPriceFilter):
            flash("From-price must be smaller than to-price")

        #formatting date filters
        if fromDateFilter:
            fD = date.fromisoformat(fromDateFilter)
        if toDateFilter:
            tD = date.fromisoformat(toDateFilter)
        
        #checks if from is less than to date
        if  fromDateFilter and toDateFilter and (not dateIsLessThan(fD, tD)):
            flash("From-date must be less than to-date")

        #floats price filters
        floatedFromPriceFilter = 0
        if fromPriceFilter:
            floatedFromPriceFilter = float(fromPriceFilter)
        floatedToPriceFilter = 0
        if toPriceFilter:
            floatedToPriceFilter = float(toPriceFilter)
        
        #gets all expenses with the FILTERS applied
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
        
        #gets total of all expenses with the FILTERS applied
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
    #get
    elif request.method == "GET":
        #Makes it so that filters are set to nothing if they are not set already.
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
    #establish connection to data base
    conn = get_db_connection()

    #gets distinct categories and methods
    categories = conn.execute("SELECT DISTINCT category FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    methods = conn.execute("SELECT DISTINCT method FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    #sets filters to nothing off the start
    categoryFilter = None
    methodFilter = None
    keywordsFilter = None
    dateFilter = None
    fromDateFilter =None
    toDateFilter = None
    fromIncomeFilter = None
    toIncomeFilter = None

    #gets all incomes
    incs = conn.execute("SELECT * FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()
    #gets total of all incomes
    total = conn.execute("SELECT SUM(income) AS sum FROM incomes WHERE user_id = ?", (session["user_id"],)).fetchall()[0]["sum"]

    #Post
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

        #checks for if from-to and singular date is on at the same time
        if dateFilter and (fromDateFilter or toDateFilter):
            flash("Cannot do from-to date at the same time as a specific date")
        
        #checks if income filters are valid
        if (fromIncomeFilter and toIncomeFilter) and float(fromIncomeFilter) > float(toIncomeFilter):
            flash("From-income must be smaller than to-income")

        #formatting date filters
        if fromDateFilter:
            fD = date.fromisoformat(fromDateFilter)
        if toDateFilter:
            tD = date.fromisoformat(toDateFilter)
        
        #checks if from is less than to date
        if  fromDateFilter and toDateFilter and (not dateIsLessThan(fD, tD)):
            flash("From-date must be less than to-date")

        #turns income filters to float
        floatedFromIncomeFilter = 0
        if fromIncomeFilter:
            floatedFromIncomeFilter = float(fromIncomeFilter)
        floatedToIncomeFilter = 0
        if toIncomeFilter:
            floatedToIncomeFilter = float(toIncomeFilter)
        
        #gets all incomes with the FILTERS applied
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
        
        #gets total of all incomes with the FILTERS applied
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
    #Get
    elif request.method == "GET":
        #Makes it so that filters are set to nothing if they are not set already.
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
    #establish connection to data base
    conn = get_db_connection()

    #Get all expenses and Incomes sorted by date ascending
    exps = conn.execute("SELECT category, date, SUM(price * quantity) FROM expenses WHERE user_id = ? GROUP BY category", (session["user_id"],)).fetchall()
    incs = conn.execute("SELECT category, date, SUM(income) FROM incomes WHERE user_id = ? GROUP BY category", (session["user_id"],)).fetchall()

    #formats the exps and incs so it can be properly turned into .json
    expsFormatted = [{'category': category, 'price': price, 'date': date} for category, date, price in exps]
    incsFormatted = [{'category': category, 'income': income, 'date': date} for category, date, income in incs]

    return render_template("pieChart.html", incomes=incsFormatted, expenses=expsFormatted)


@app.route("/lineChart", methods=["GET", "POST"])
@login_required
def lineChart():
    #establish connection to data base
    conn = get_db_connection()

    #Get all expenses and Incomes sorted by date ascending
    exps = conn.execute("SELECT price, category, date FROM expenses WHERE user_id = ? ORDER BY date ASC", (session["user_id"],)).fetchall()
    incs = conn.execute("SELECT income, category, date FROM incomes WHERE user_id = ? ORDER BY date ASC", (session["user_id"],)).fetchall()

    #formats the exps and incs so it can be properly turned into .json
    expsFormatted = [{'price': price, 'category' : category, 'date': date} for price, category, date in exps]
    incsFormatted = [{'income': income, 'category' : category, 'date': date} for income, category, date in incs]

    #gets all distinct incs and exps categories
    expsCategories = conn.execute("SELECT DISTINCT category from expenses WHERE user_id = ?", (session["user_id"],)).fetchall()
    incsCategories = conn.execute("SELECT DISTINCT category from incomes WHERE user_id = ?", (session["user_id"],)).fetchall()

    #gets all the years
    years = set(datetime.strptime(element['date'], "%Y-%m-%d").year for element in (expsFormatted + incsFormatted))
    #sorts the years
    sortedYears = sorted(list(years))
    
    return render_template("lineChart.html", incomes=incsFormatted, expenses=expsFormatted, years=sortedYears, expsCategories=expsCategories, incsCategories=incsCategories)