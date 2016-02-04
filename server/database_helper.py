import sqlite3

from flask import g

DATABASE = "database.db"
DATABASE_SCHEMA = "database.schema"

def init_db():
    db = connect_db()
    with db:
        cur = db.cursor()
        with open(DATABASE_SCHEMA, mode='r') as f:
            cur.executescript(f.read())
        cur.close()
        db.commit()

def connect_db():
    return sqlite3.connect(DATABASE)

def close_db():
    g.db.close()


def sign_in(email, password):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""SELECT * FROM Users WHERE email = ? AND password = ?""",
                        (email, password,))
            status = len(cur.fetchall())
            cur.close()
            g.db.commit()
        except sqlite3.Error as e:
            return False

    if status != 1:
        return False

    return True

def insert_token(email, token):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""INSERT INTO UserTokens (email, token)
                           VALUES (?, ?)""",
                           (email, token,))
            cur.close()
            g.db.commit()
        except sqlite3.Error:
            return False

        return True

def sign_up(email, password, firstname,
            familyname, gender, city,
            country):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""INSERT INTO Users (email, password, firstname, familyname, gender, city, country)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (str(email), password, firstname, familyname, gender, city, country,))
            cur.close()
            g.db.commit()
        except sqlite3.Error:
            return False

        return True


def sign_out(token):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""DELETE FROM UserTokens WHERE token = ?""",
                                 (token,)).rowcount
            cur.close()
            g.db.commit()
        except sqlite3.Error as e:
            print(e.message)
            return False

        if status != 1:
            return False

        return True

def get_email_from_token(token):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""SELECT email FROM UserTokens WHERE token = ?""",
                                 (token,)).fetchall()
            cur.close()
            g.db.commit()
        except sqlite3.Error as e:
            print(e.message)
            return ""

        if status:
            return str(status[0][0])

        return ""

def change_password_helper(email, old_password, new_password):
    with g.db:
            cur = g.db.cursor()
            try:
                status = cur.execute("""UPDATE Users SET password = ? WHERE email = ? AND password = ?""",
                                    (new_password, email, old_password,)).rowcount
                cur.close()
                g.db.commit()
            except sqlite3.Error as e:
                print(e.message)
                return False

    if status != 1:
        return False

    return True

def change_password(token, old_password,
                    new_password):
    email = get_email_from_token(token)

    if email:
        if change_password_helper(email, old_password, new_password):
            return 1
        else:
            return 2

    return 3

def get_user_data_by_token(token):
    return get_user_data_by_email(token, get_email_from_token(token))

def get_user_data(email):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""SELECT * FROM Users WHERE email = ?""",
                                 (email,)).fetchall()
            cur.close()
            g.db.commit()
        except sqlite3.Error as e:
            print(e.message)
            return ()

    if status:
        return status[0]

    return ()


def get_user_data_by_email(token, email):
    if email and email == get_email_from_token(token):
        data = get_user_data(email)

        if data:
            match = \
            {
            'email': data[0],
            'firstname': data[2],
			'familyname': data[3],
			'gender': data[4],
			'city': data[5],
			'country': data[6],
		    }
            return {"success": True, "message": "User data retrieved.", "data": match}
        return {"success": False, "message": "No such user."}
    return {"success": False, "message": "You are not signed in."}


def get_user_messages_by_token(token):
    return get_user_messages_by_email(token, get_email_from_token(token))

def get_messages(email):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""SELECT Writer, Message FROM UserMessages WHERE email = ?""",
                                 (email,)).fetchall()
            cur.close()
            g.db.commit()
        except sqlite3.Error as e:
            print(e.message)
            return ()

    if status:
        return status

    return ()

def user_exist(email):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""SELECT * FROM Users WHERE email = ?""", (email,))
            status = len(cur.fetchall())
            cur.close()
            g.db.commit()
        except sqlite3.Error as e:
            print(e.message)
            return False

    if status != 1:
        return False

    return True

def get_user_messages_by_email(token, email):
    if get_email_from_token(token):
        if not user_exist(email):
            return {"success": False, "message": "No such user."}

        messages = get_messages(email)
        data = [{"writer": writer, "message": message} for writer, message in messages]

        return {"success": True, "message": "User messages retrieved.", "data": data}
    return {"success": False, "message": "You are not signed in."}


def post_message_helper(email, writer, message):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""INSERT INTO UserMessages (email, writer, message)
                           VALUES (?, ?, ?)""",
                           (email, writer, message,))
            cur.close()
            g.db.commit()
        except sqlite3.Error:
            return False

        return True

def post_message(token, message, email):
    if gget_email_from_token(token):
        if not user_exist(email):
            return {"success": False, "message": "No such user."}

        if post_message_helper(email, get_email_from_token(token), message):
             return {"success": True, "message": "Message posted"}

    return {"success": False, "message": "You are not signed in."}
