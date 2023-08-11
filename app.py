import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required, apology


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

        db.execute("INSERT INTO birthdays(name, month, day) VALUES(?,?,?)", (name, month, day))
        con.commit()
        return redirect("/")

    else:

        # TODO: Display the entries in the database on index.html
        birthdays = db.execute("SELECT * FROM birthdays")
        return render_template("index.html", birthdays = birthdays)

@app.route("/login", methods = ["GET", "POST"])
def login():
    

