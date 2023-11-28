from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3 
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignupForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
DATABASE = 'database.db'

#DB connect
def get_connection():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn

#DB table
def make_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT)')
    conn.commit()
    conn.close()

#Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hashed_password = generate_password_hash(password)

        if register_user_db(name, email, hashed_password):
            raise Exception('Succes')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

#Registrer bruger i DB
def register_user_db(name, email, hashed_password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
        conn.commit()
        return True 
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")
        return False
    finally: 
        conn.close()


#app run
if __name__=="__main__":
    app.run(host='0.0.0.0', port=80, debug=True)