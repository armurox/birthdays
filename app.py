import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required, apology
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
con = sqlite3.connect("birthdays.db", check_same_thread=False)
con.row_factory = sqlite3.Row
db = con.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        # Add the user's entry into the database
        name = request.form.get("name")
        while True:
            try:
                month = int(request.form.get("month"))
                day = int(request.form.get("day"))
            except ValueError:
                pass
            if (month > 0 and month < 13 and day > 0 and day < 32):
                break
            else:
                continue

        db.execute("INSERT INTO birthdays(user_id, name, month, day) VALUES(?,?,?,?)", (session["user_id"], name, month, day))
        con.commit()
        return redirect("/")

    else:

        # TODO: Display the entries in the database on index.html
        birthdays = db.execute("SELECT * FROM birthdays WHERE user_id = (?)", (session["user_id"],))
        return render_template("index.html", birthdays = birthdays)

@app.route("/login", methods = ["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"),))

        rows = [dict(i) for i in rows]
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return ("Please provide a username", 400)
        database_username = db.execute("SELECT username FROM users WHERE username = (?)", (username,))
        database_username = [dict(i) for i in database_username]
        if (
            len(database_username)
            > 0
        ):
            return apology("username already exists", 400)
        password = request.form.get("password")
        password_check = request.form.get("confirmation")
        if password != password_check or not password:
            return apology("passwords do not match / did not enter a password", 400)
        # Register user
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username,generate_password_hash(password)))
        con.commit()
        user = db.execute("SELECT id FROM users WHERE username = (?)", (username,))
        user = [dict(i) for i in user]
        # Log user in  after registration
        session["user_id"] = user[0]["id"]
        flash("Registered!")
        return redirect("/")

    else:
        return render_template("register.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")