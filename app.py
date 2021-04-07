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
            cur = db.cursor()
            primaryKey = query_db('SELECT id FROM users WHERE name = ?', [anonForm['instructor']], one=True)['id']
            cur.execute('INSERT INTO feedbackAns VALUES (?, ?, ?, ?, ?)', [primaryKey, anonForm['qn0'], anonForm['qn1'], anonForm['qn2'], anonForm['qn3']])
            db.commit()
            cur.close()
        return render_template("feedback.html", usertype=escape(usertype), instructors=instructorNames, questions=feedbackQn, len=len(feedbackQn))
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

def get_student_grades(username):
    grades = []
    for i in range(5):
        grades.append("Not graded yet")
    result = query_db('SELECT MAX(quiz1) FROM marks WHERE student_username = ?', [username], one=True)
    grades[0] = result[0] if result[0]  else "Not graded yet"
    print(grades[0])
    result = query_db('SELECT MAX(quiz2) FROM marks WHERE student_username = ?', [username], one=True)
    grades[1] = result[0] if result[0]  else "Not graded yet"

    result = query_db('SELECT MAX(quiz3) FROM marks WHERE student_username = ?', [username], one=True)
    grades[2] = result[0] if result[0]  else "Not graded yet"

    result = query_db('SELECT MAX(midtermexam) FROM marks WHERE student_username = ?', [username], one=True)
    grades[3] = result[0] if result[0]  else "Not graded yet"

    result = query_db('SELECT MAX(finalexam) FROM marks WHERE student_username = ?', [username], one=True)
    grades[4] = result[0] if result[0] else "Not graded yet"

    return grades

def get_current_username():
    result = query_db('SELECT username FROM users WHERE id = ?', args=[session['userID']], one=True)
    return result[0]

def get_current_name():
    result = query_db('SELECT name FROM users WHERE id = ?', args=[session['userID']], one=True)
    return result[0]

def get_current_usertype():
    result = query_db('SELECT usertype FROM users WHERE id = ?', args=[session['userID']], one=True)
    return result[0]

@app.route("/grades")
def grades():
    if 'userID' in session:
        usertype = get_current_usertype()

        if usertype=="Student":
            username = get_current_username()
            grades = get_student_grades(username)
            return render_template('grades_student.html',grades=grades)
        elif usertype=='Instructor':
            student_list = query_db("SELECT username FROM users WHERE usertype = 'Student'", args=(), one=False)
            r_requests = query_db("SELECT student_username,test FROM requests", args=(), one=False)

            remark_requests = {}
            for r in r_requests:
                if r[0] not in remark_requests:
                    remark_requests[r[0]] = []
                remark_requests[r[0]].append(r[1])


            mark_book = {}
            for s in student_list:
                grades = get_student_grades(s[0])
                mark_book[s[0]] = grades

            return render_template('grades_teacher.html',mark_book=mark_book,remark_requests=remark_requests)

    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
