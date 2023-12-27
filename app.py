from flask import (
    Flask, redirect, url_for, render_template,
    request, session, flash, abort, send_from_directory
)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from forms import SignupForm, LoginForm, PostForm, FitnessForm
from datetime import datetime
import models
import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['UPLOAD_FOLDER'] = 'uploads'

    # Vi laver vores eget custom filter for dato og bruger Python's datetime
    def datetime_format(value):
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        return date_obj.strftime("%d %B")

    app.jinja_env.filters['datetimeformat'] = datetime_format

    # Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard", methods=['GET', 'POST'])
    def dashboard():
        if not is_logged_in():
            flash('Du skal være logget ind for at tilgå dashboard', 'error')
            return redirect(url_for('login'))

        user_id = session['user_id']
        user_id = session['user_id']
        rewards = models.get_rewards()
        users_rewards = models.get_users_rewards(user_id)
        challenges = models.get_users_challenges(user_id)
        user_posts = models.get_users_posts(user_id)
        follows = models.get_users_follow(user_id)
        users_fitness = models.get_users_fitness(user_id)
        form = FitnessForm()
        # Hent navnet på title feltet i vores rewards,
        # hvis der er nogle associeret i users_rewards, ellers er den empty
        users_rewards = [reward[0] for reward in users_rewards] \
            if users_rewards else []

        if request.method == 'POST':
            if form.validate_on_submit():
                distance = form.distance.data
                calories_burned = form.calories.data
                models.add_fitness_data(user_id, distance, calories_burned)
                flash('Data uploadet', 'success')
                return redirect(url_for('dashboard'))
            # Vi laver redirect med det nye data,
            # og undgår resubmission når refresh af siden sker.
            else:
                flash('Data kunne ikke uploades', 'error')
        # Vi render det hele med template, og tjekker med if i vores template
        return render_template(
            "dashboard.html",
            form=form,
            rewards=rewards,
            users_rewards=users_rewards,
            challenges=challenges,
            user_posts=user_posts,
            follows=follows,
            users_fitness=users_fitness
        )

    @app.route("/dashboard/<int:post_id>", methods=['DELETE'])
    def delete_dashboard_post(post_id):
        if models.delete_post_db(post_id, session['user_id']):
            return ''
        else:
            abort(403)

    @app.route("/dashboard/unfollow/<int:friends_id>", methods=['DELETE'])
    def unfollow_users(friends_id):

        users_id = session['user_id']

        if models.unfollow_user(users_id, friends_id):
            return '', 204
        else:
            flash('Handling fejlede', 'error')
            abort(403)

    # Login
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            if models.validate_user(email, password):
                session['email'] = email
                # Hent id og navn på bruger
                conn = models.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               SELECT id, name FROM users WHERE email = ?
                               ''', (email,))
                user = cursor.fetchone()
                conn.close()
                # Brug info i session
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

    def is_logged_in():  # Check om email er inkluderet i vores session
        return 'email' in session

    # Signup
    @app.route("/signup", methods=['GET', 'POST'])
    def signup():
        form = SignupForm()
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            hashed_password = generate_password_hash(password)
            # Check for eksisterende email
            if models.check_for_emails(email):
                flash('Den indtastede email er allerede i brug', 'error')
                return render_template('signup.html', form=form)
            # Hvis alt er godkendt
            if models.register_user_db(name, email, hashed_password):
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

        challenges = models.get_challenges()

        if challenges:
            return render_template("challenges.html", challenges=challenges)
        else:
            no_challenges_found = "Der er i øjeblikket ingen udfordringer"
            return render_template(
                "challenges.html", no_challenges_found=no_challenges_found)

    # join challenge
    @app.route("/join_challenge/<int:challenges_id>", methods=['POST'])
    def join_challenge(challenges_id):
        user_id = session.get('user_id')

        if models.check_joined_challenges(user_id, challenges_id):
            flash('Du er allerede tilmeldt denne udfordring', 'error')
        else:
            models.join_challenge_action(user_id, challenges_id)

        return redirect(url_for('challenges'))

    @app.route("/feed", methods=['GET', 'POST'])
    def feed():
        if not is_logged_in():
            flash('Du skal være logget ind for at tilgå feed', 'error')
            return redirect(url_for('login'))
        return render_template("feed.html")

    @app.route("/people", methods=['GET', 'POST'])
    def people():
        if not is_logged_in():
            flash('Du skal være logget ind for at tilgå feed', 'error')
            return redirect(url_for('login'))

        if request.method == 'POST':
            search = request.form['search']
            users = models.get_users(search)
        else:
            users = models.get_users()

        return render_template("people.html", users=users)

    # Tilføj venner og fjern venner
    @app.route("/people/<int:friends_id>", methods=['POST'])
    def follow_users(friends_id):

        users_id = session['user_id']

        if models.check_existing_follow(users_id, friends_id):
            flash('Du følger allerede denne person', 'error')
        else:
            models.follow_user(users_id, friends_id)
            flash('Person tilføjet', 'success')

        return redirect(url_for('people'))

    @app.route("/posts", methods=['GET', 'POST'])
    def posts():
        if not is_logged_in():
            flash('Du skal være logget ind for at tilgå feed', 'error')
            return redirect(url_for('login'))

        form = PostForm()
        users_id = session['user_id']

        if request.method == 'POST':
            # Håndter søge funktionalitet
            search = request.form.get('search')
            if search:
                search_post = models.get_posts(search)
                if search_post:
                    return render_template(
                        "posts.html", posts_data=search_post, form=form)
                else:
                    flash('Ingen resultater fundet', 'error')
                    return render_template(
                        "posts.html", posts_data=[], form=form)

            # Håndter oprettelsen af post
            if form.validate_on_submit():
                content = form.content.data
                file = request.files.get('image_path')

                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], filename))
                    image_path = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename)
                    models.make_post(users_id, content, image_path)
                    flash('Opslag oprettet', 'success')
                else:
                    models.make_post(users_id, content)
                    flash('Opslag oprettet', 'success')

                return redirect(url_for('posts'))

        # Hent opslag eller fejl.
        posts_data = models.get_posts()
        if posts_data:
            return render_template(
                "posts.html", posts_data=posts_data, form=form)
        else:
            flash('Ingen opslag i øjeblikket', 'error')
            return render_template("posts.html", form=form)

    # Image
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route("/posts/<int:post_id>", methods=['DELETE'])
    def delete_post(post_id):
        if models.delete_post_db(post_id, session['user_id']):
            return ''
        else:
            abort(403)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for('index'))

    return app


# app run
if __name__ == "__main__":
    create_app().run(host='0.0.0.0', port=80, debug=True)
