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
                 'topic TEXT, '
                 'participants INTEGER, '
                 'reward_id INTEGER, '
                 'FOREIGN KEY(reward_id) REFERENCES rewards(id)'
                 ')')
    conn.commit()
    conn.close()

#Hent oplysninger
def get_rewards(users_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_rewards WHERE users_id = ?', (users_id,))
    rewards = cursor.fetchall()
    conn.close()

    if rewards:
            return rewards #Der er et match
    return None #Intet match

def get_challenges():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM challenges')
    challenges = cursor.fetchone()
    conn.close()

    if challenges:
            return challenges #Der er et match
    return None #Intet match

#Opret udfordringer
def make_challenge(name, topic, participants, reward_id=None):
    conn = get_connection()

    if reward_id is None:
        query =  'INSERT INTO challenges (name, topic, participants) VALUES (?, ?, ?)'
        values = (name, topic, participants)
    else: 
        query = 'INSERT INTO challenges (name, topic, participants, reward_id) VALUES (?, ?, ?, ?)'
        values = (name, topic, participants, reward_id)
    
    conn.execute(query, values)
    conn.commit()
    conn.close()

#Antal af deltagere i en challenge
def count_participants():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM challenges')
    count = cursor.fetchone()[0]

    conn.close()
    return count

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

friends_table()
posts_table()
groups_table()
users_groups()
users_rewards()
rewards_table()
challenges_table()