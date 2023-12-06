from flask import Flask, redirect, url_for, render_template, request, session, flash 
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignupForm, LoginForm
from models import get_connection, get_rewards, validate_user, check_for_emails, register_user_db 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

#Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        flash('Du skal være logget ind for at tilgå dashboard', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    rewards = get_rewards(user_id)

    if rewards: 
        return render_template("dashboard.html", rewards=rewards)
    else:
        no_rewards_found = "Du har ingen belønninger endnu"
        return render_template("dashboard.html", no_rewards_found=no_rewards_found)

#Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if validate_user(email, password):
            session['email'] = email
            #Hent id og navn på bruger
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            conn.close()
            #Brug info i session
            if user:
                user_id = user['id']
                user_name = user['name']
                session['user_id'] = user_id
                session['name'] = user_name
            else: 
                flash('Navn ikke fundet', 'error')

            return redirect(url_for('dashboard'))
        else:
            flash('Email eller password matchede ikke, prøv igen', 'error')
            return redirect(url_for('login'))
        
    return render_template('login.html', form=form)

def is_logged_in(): #Check om email er inkluderet i vores session
    return 'email' in session

#Signup
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hashed_password = generate_password_hash(password)
        #Check for eksisterende email
        if check_for_emails(email):
            flash('Den indtastede email er allerede i brug', 'error')
            return render_template('signup.html', form=form)
        #Hvis alt er godkendt
        if register_user_db(name, email, hashed_password):
            flash('Registrering godkendt', 'succes')
            return redirect(url_for('login'))
        else: 
            flash('Registrering mislykkedes, prøv igen', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html', form=form)

@app.route("/challenges")
def challenges():
    if not is_logged_in():
        flash('Du skal være logget ind for at tilgå dashboard', 'error')
        return redirect(url_for('login'))
    return render_template("challenges.html")

@app.route("/feed")
def feed():
    if not is_logged_in():
        flash('Du skal være logget ind for at tilgå feed', 'error')
        return redirect(url_for('login'))
    return render_template("feed.html")

@app.route("/people")
def people():
    if not is_logged_in():
        flash('Du skal være logget ind for at tilgå feed', 'error')
        return redirect(url_for('login'))
    return render_template("people.html")

@app.route("/posts")
def posts():
    if not is_logged_in():
        flash('Du skal være logget ind for at tilgå feed', 'error')
        return redirect(url_for('login'))
    return render_template("posts.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

#app run
if __name__=="__main__":
    app.run(host='0.0.0.0', port=80, debug=True)