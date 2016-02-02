import sqlite3

DATABASE = "database.db"

def init_db():
    db = connect_db()
    with db:
        cur = db.cursor()
        with open('database.schema', mode='r') as f:
            cur.executescript(f.read())
        cur.close()
        db.commit()

def connect_db():
    return sqlite3.connect(DATABASE)

def close_db():
    raise NotImplementedError

def sign_in(email, password):
    raise NotImplementedError

def sign_up(email, password, firstname,
            familyname, gender, city,
            country):
    db = connect_db()
    with db:
        cur = db.cursor()
        cur.execute("""INSERT INTO Users (email, password, firstname, familyname, gender, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)""", \
                    (email, password, firstname, familyname, gender, city, country,))
        cur.close()
        db.commit()


def sign_out(token):
    raise NotImplementedError

def change_password(token, old_password,
                    new_password):
    raise NotImplementedError

def get_user_data_by_token(token):
    raise NotImplementedError

def get_user_data_by_email(token, email):
    raise NotImplementedError

def get_user_messages_by_token(token):
    raise NotImplementedError

def get_user_messages_by_email(token, email):
    raise NotImplementedError

def post_message(token, message, email):
    raise NotImplementedError