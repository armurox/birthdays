import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
con = sqlite3.connect("birthdays.db", check_same_thread=False)
con.row_factory = sqlite3.Row
db = con.cursor()

@app.route("/", methods=["GET", "POST"])
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


