from flask import Flask, redirect, url_for, render_template, request, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignupForm, LoginForm, PostForm
from models import get_connection, get_rewards, get_challenges, get_users_challenges, validate_user, check_for_emails, register_user_db, join_challenge_action, check_joined_challenges, get_posts, make_post, delete_post_db, get_users_posts

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
    
    user_id = session['user_id']
    rewards = get_rewards(user_id)
    challenges = get_users_challenges(user_id)
    user_posts = get_users_posts(user_id)

    no_rewards_found = "Du har ingen belønninger endnu"
    no_challenges_found = "Du har ingen udfordringer endnu"
    no_posts_found = "Du har ingen opslag endnu"

    if rewards and challenges and user_posts:
        return render_template("dashboard.html", rewards=rewards, challenges=challenges, user_posts=user_posts)

    if not (rewards or challenges or user_posts):
        return render_template("dashboard.html", no_rewards_found=no_rewards_found, no_challenges_found=no_challenges_found, no_posts_found=no_posts_found)
    else:
        if not user_posts:
            return render_template("dashboard.html", rewards=rewards, challenges=challenges, no_posts_found=no_posts_found)
        if not challenges:
            return render_template("dashboard.html", rewards=rewards, no_challenges_found=no_challenges_found, user_posts=user_posts)
        if not rewards:
            return render_template("dashboard.html", no_rewards_found=no_rewards_found, challenges=challenges, user_posts=user_posts)

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
    
    challenges = get_challenges()

    if challenges: 
        return render_template("challenges.html", challenges=challenges)
    else:
        no_challenges_found = "Der er i øjeblikket ingen udfordringer"
        return render_template("challenges.html", no_challenges_found=no_challenges_found)

#join challenge
@app.route("/join_challenge/<int:challenges_id>", methods=['POST'])
def join_challenge(challenges_id):
    user_id = session.get('user_id')

    if check_joined_challenges(user_id, challenges_id):
        flash('Du er allerede tilmeldt denne udfordring', 'error')
    else: 
        join_challenge_action(user_id, challenges_id)

    return redirect(url_for('challenges'))


@app.route("/feed", methods=['GET', 'POST'])
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


@app.route("/posts", methods=['GET', 'POST'])
def posts():
    if not is_logged_in():
        flash('Du skal være logget ind for at tilgå feed', 'error')
        return redirect(url_for('login'))
    
    form = PostForm()
    users_id = session['user_id']
    
    if request.method =='POST':
        if form.validate_on_submit():
            content = form.content.data
            make_post(users_id, content)
            flash('Opslag oprettet')
            return redirect(url_for('posts'))
        else:
            flash('Noget gik galt')
            return render_template("posts.html", form=form, posts_data=posts_data)

    posts_data = get_posts()
    if posts_data: 
        return render_template("posts.html", posts_data=posts_data, form=form)
    else: 
        flash('Ingen opslag i øjeblikket', 'error')
        return render_template("posts.html", form=form)

@app.route("/posts/<int:post_id>", methods=['DELETE'])  
def delete_post(post_id):
    if delete_post_db(post_id, session['user_id']):
        return ''
    else:
        abort(403)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

#app run
if __name__=="__main__":
    app.run(host='0.0.0.0', port=80, debug=True)