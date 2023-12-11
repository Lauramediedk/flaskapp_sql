from flask import Flask
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from config import DATABASE

#DB connect
def get_connection():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn

#DB tables
def make_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                 'name TEXT, '
                 'email TEXT, '
                 'password TEXT)'
                 )
    conn.commit()
    conn.close()

def friends_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS friends('
                 'users_id INTEGER, '
                 'friends_id INTEGER, '
                 'FOREIGN KEY(users_id) REFERENCES users(id), '
                 'FOREIGN KEY(friends_id) REFERENCES users(id)'
                 ')')
    conn.commit()
    conn.close()

def posts_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS posts('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                 'users_id INTEGER, '
                 'content TEXT, '
                 'created DATETIME DEFAULT CURRENT_TIMESTAMP, '
                 'FOREIGN KEY(users_id) REFERENCES users(id)'
                 ')')
    conn.commit()
    conn.close()

def groups_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS groups('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' 
                 'created DATETIME DEFAULT CURRENT_TIMESTAMP, ' 
                 'author_id INTEGER, ' 
                 'FOREIGN KEY(author_id) REFERENCES users(id)'
                 ')')
    conn.commit()
    conn.close()

def users_groups():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users_groups('
                 'users_id INTEGER, '
                 'group_id INTEGER, '
                 'FOREIGN KEY(users_id) REFERENCES users(id), '
                 'FOREIGN KEY(group_id) REFERENCES groups(id)'
                 ')')
    conn.commit()
    conn.close()

def users_rewards():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users_rewards('
                 'users_id INTEGER, '
                 'rewards_id INTEGER, '
                 'FOREIGN KEY(users_id) REFERENCES users(id), '
                 'FOREIGN KEY(rewards_id) REFERENCES rewards(id)'
                 ')')
    conn.commit()
    conn.close()

def rewards_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS rewards('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' 
                 'title TEXT, '
                 'description TEXT' 
                 ')')
    conn.commit()
    conn.close()

def challenges_table():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS challenges('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' 
                 'name TEXT, '
                 'created DATETIME DEFAULT CURRENT_TIMESTAMP, ' 
                 'end_date DATETIME DEFAULT (datetime("now", "+30 days")), '
                 'topic TEXT, '
                 'participants INTEGER, '
                 'reward_id INTEGER, '
                 'FOREIGN KEY(reward_id) REFERENCES rewards(id)'
                 ')')
    conn.commit()
    conn.close()

def users_challenges():
    conn = get_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users_challenges('
                 'users_id INTEGER, '
                 'challenges_id INTEGER, '
                 'FOREIGN KEY(users_id) REFERENCES users(id), '
                 'FOREIGN KEY(challenges_id) REFERENCES challenges(id)'
                 ')')
    conn.commit()
    conn.close()

#Handlinger
################################################################################

#Hent oplysninger om brugerens specifikke challenges og benyt count her til antal af deltagere
def get_users_challenges(users_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT challenges.*, COUNT(users_challenges.users_id) AS participants_count
                   FROM users_challenges
                   INNER JOIN challenges ON users_challenges.challenges_id = challenges_id
                   WHERE users_challenges.users_id = ?
                   GROUP BY challenges.id
                   ''',(users_id,))
    challenges = cursor.fetchall()
    conn.close()

    if challenges:
            return challenges #Der er et match
    return None #Intet match


#Hent udfordringer fra databasen og find antal deltagere
def get_challenges():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT challenges.id,
                   challenges.name,
                   challenges.created,
                   challenges.end_date,
                   challenges.topic,  
                   COUNT(users_challenges.users_id) AS participants_count 
                   FROM challenges  
                   LEFT JOIN users_challenges ON challenges.id = users_challenges.challenges_id 
                   GROUP BY challenges.id
                   ''')
    challenges = cursor.fetchall()
    conn.close()

    if challenges:
        return challenges #Der er et match
    return None #Intet match


#Brugere kan deltage i challenges når de klikker deltag
def join_challenge_action(users_id, challenges_id):
    conn = get_connection()
    query =  'INSERT INTO users_challenges (users_id, challenges_id) VALUES (?, ?)'
    conn.execute(query, (users_id, challenges_id))
    conn.commit()
    conn.close()


#Hent belønninger
def get_rewards(users_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_rewards WHERE users_id = ?', (users_id,))
    rewards = cursor.fetchall()
    conn.close()

    if rewards:
        return rewards #Der er et match
    return None #Intet match


def get_posts(): #We fetch the users name also
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT posts.id, posts.users_id, posts.content, posts.created, users.name '
                   'FROM posts '
                   'INNER JOIN users ON posts.users_id = users.id')
    posts = cursor.fetchall()
    conn.close()

    return posts   

def get_users_posts(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE users_id = ?', (user_id,))
    user_posts = cursor.fetchall()
    conn.close()

    return user_posts


def delete_post_db(post_id, user_id): #Tjek først om post eksisterer og matcher med brugeren
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = ? AND users_id = ?', (post_id, user_id))
    post = cursor.fetchone()

    if post:
        cursor.execute('DELETE FROM posts WHERE id = ? AND users_id = ?', (post_id, user_id))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False
    
    
#Validering
def validate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()  # Fetch the hashed password
    conn.close()

    if result:
        hashed_password = result[0]
        if check_password_hash(hashed_password, password):
            return True #Passwords matcher
        return False #Intet match med password eller user
    
#Email validering for signup
def check_for_emails(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()

    if result:
        print("Existing email found:", email)
        return True

    return False


def check_joined_challenges(users_id, challenges_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_challenges WHERE users_id = ? AND challenges_id = ?', (users_id, challenges_id))
    result = cursor.fetchone()
    conn.close()

    if result:
        return True

    return False

# Indsæt
################################################################################

#Lav post opslag
def make_post(users_id, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO posts (users_id, content) VALUES (?, ?)', (users_id, content,))
    conn.commit()
    conn.close()


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

#Lav tables
#################################################################################

friends_table()
posts_table()
groups_table()
users_groups()
users_rewards()
rewards_table()
challenges_table()
users_challenges()