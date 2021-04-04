# required imports
# the sqlite3 library allows us to communicate with the sqlite database
import sqlite3
# we are adding the import 'g' which will be used for the database
from flask import Flask, render_template, request, g, session, redirect, url_for, escape

# the database file we are going to communicate with
DATABASE = 'logindatabase.db'

# connects to the database
def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
# (don't worry if you don't understand this code)
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# tells Flask that "this" is the current running app
app = Flask(__name__)
app.secret_key = b'abbas'

# this function gets called when the Flask app shuts down
# tears down the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        results = query_db('SELECT * FROM users', args=(), one=False)
        formStatus = isFormFilled(request.form, {'username': "Username", 'password': "Password"})
        if len(formStatus) != 0: return render_template('login.html', msg=formStatus)
        for result in results:
            if result[1] == request.form['username']:
                if result[2] == request.form['password']:
                    session['userID'] = result[0]
                    return redirect(url_for('index'))
        return render_template('login.html', msg="Incorrect UserName/Password")
    elif 'userID' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html', msg="")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    if request.method == 'POST':
        accInfo = request.form
        formStatus = isFormFilled(accInfo, {'name': "Name", 'usertype': "User type", 'username': "Username", 'password': "Password"})
        if len(formStatus) != 0: return render_template('signup.html', msg=formStatus)
        result = query_db('SELECT * FROM users WHERE username = ?', [accInfo['username']], one=True)
        if result == None:
            if isStrongPassword(accInfo['username'], accInfo['password']):
                primaryKey = query_db('SELECT max(id) AS currID FROM users', one=True)['currID'] + 1
                cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', [primaryKey, accInfo['username'], accInfo['password'], accInfo['name'], accInfo['usertype']])
                db.commit()
                cur.close()
                return render_template('signup.html', msg="An account has been made")
            else:
                return render_template('signup.html', msg="Low Password Strength")
        else:
            return render_template('signup.html', msg="Not unique username")
    return render_template('signup.html', msg="")


def isFormFilled(accInfo, keyMap):
    for key in keyMap.keys():
        if (key not in accInfo) or (len(accInfo[key]) == 0):
            return str(keyMap[key]) + " is missing"
    return ""


def isStrongPassword(username, password):
    (numOfLower, numOfUpper, numOfSym, numOfDig) = (0, 0, 0, 0)
    if len(password) >= 8:
        for i in password:
            if i.isdigit():
                numOfDig += 1
            if i.islower():
                numOfLower += 1
            if i.isupper():
                numOfUpper += 1
            if i == '@' or i == '$' or i == '_':
                numOfSym += 1
    if numOfLower >= 1 and numOfUpper >= 1 and numOfSym >= 1 \
            and numOfDig >= 1 and numOfLower + numOfUpper + numOfSym \
            + numOfDig == len(password) and username != password:
        return True
    return False


@app.route('/')
def index():
    if 'userID' in session:
        db = get_db()
        db.row_factory = make_dicts
        results = query_db('SELECT name, usertype FROM users WHERE id = ?', [session['userID']], one=True)
        return render_template('index.html', name=escape(results['name']) , usertype=escape(results['usertype']))
    return redirect(url_for('login'))


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


@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    db = get_db()
    db.row_factory = make_dicts
    usertype = query_db('SELECT name, usertype FROM users WHERE id = ?', [session['userID']], one=True)['usertype']
    if usertype == "Student":
        instructorNames = [instructorDict['name'] for instructorDict in query_db('SELECT name FROM users WHERE usertype = ?', ['Instructor'])]
        feedbackQn = [questionsDict['question'] for questionsDict in query_db('SELECT question FROM feedbackQn') ]
        if request.method == "POST":
            anonForm = request.form
            formStatus = isFormFilled(anonForm, {
                'instructor': "Instructor",
                'qn0': "Question 0",
                'qn1': "Question 1",
                'qn2': "Question 2",
                'qn3': "Question 3",
            })
            if len(formStatus) != 0: 
                return render_template("feedback.html", usertype=escape(usertype), instructors=instructorNames, questions=feedbackQn, len=len(feedbackQn), msg=formStatus)
            else:
                cur = db.cursor()
                primaryKey = query_db('SELECT id FROM users WHERE name = ?', [anonForm['instructor']], one=True)['id']
                cur.execute('INSERT INTO feedbackAns VALUES (?, ?, ?, ?, ?)', [primaryKey, anonForm['qn0'], anonForm['qn1'], anonForm['qn2'], anonForm['qn3']])
                db.commit()
                cur.close()
        return render_template("feedback.html", usertype=escape(usertype), instructors=instructorNames, questions=feedbackQn, len=len(feedbackQn), msg="")
    elif usertype == "Instructor":
        feedbackQn = [questionsDict for questionsDict in query_db('SELECT * FROM feedbackQn')]
        results = query_db('SELECT * FROM feedbackAns WHERE id = ?', [session['userID']])
        results = ["None"] if len(results) == 0 else results
        return render_template("feedback.html", usertype=escape(usertype), questions=feedbackQn, len=len(feedbackQn), answers=results)
    
@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/links")
def links():
    return render_template("links.html")


@app.route('/logout')
def logout():
    session.pop('userID', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
