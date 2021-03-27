import sqlite3
from flask import Flask, render_template, request, g

app = Flask(__name__)

DATABASE = './assignment3.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/lectures")
def lectures():
    return render_template("lectures.html")

@app.route("/labs")
def labs():
    return render_template("labs.html")

@app.route("/assignments")
def assignments():
    return render_template("assignments.html")

@app.route("/tests")
def tests():
    return render_template("tests.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/links")
def links():
    return render_template("links.html")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=True)