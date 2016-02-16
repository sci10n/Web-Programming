import random
import sqlite3

from flask import g

DATABASE = "database.db"
DATABASE_SCHEMA = "database.schema"

SUCCESS = 1
NO_SUCH_USER = 2
NOT_SIGNED_IN = 3
WRONG_PASSWORD = 4
WRONG_USERNAME_PASSWORD = 5
USER_ALREADY_EXIST = 6


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
    if hasattr(g, "gb"):
        g.db.close()


def sign_in(email, password):
    if not sign_in_helper(email, password):
        return WRONG_USERNAME_PASSWORD, None

    token = generate_token()
    while not insert_token(email, token):
        token = generate_token()

    return SUCCESS, token


def sign_in_helper(email, password):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""SELECT * FROM Users WHERE email = ? AND password = ?""",
                        (email, password,))
            status = len(cur.fetchall())
            cur.close()
        except sqlite3.Error:
            return False

    if status != 1:
        return False

    return True


def generate_token():
    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""

    for i in range(36):
        token += letters[random.randint(0, len(letters) - 1)]

    return token


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
    if sign_up_helper(email, password, firstname, familyname,
                      gender, city, country):
        return SUCCESS

    return USER_ALREADY_EXIST


def sign_up_helper(email, password, firstname,
            familyname, gender, city,
            country):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""INSERT INTO Users (email, password, firstname, familyname, gender, city, country)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (email, password, firstname, familyname, gender, city, country,))
            cur.close()
            g.db.commit()
        except sqlite3.Error:
            return False

    return True


def sign_out(token):
    if sign_out_helper(token):
        return SUCCESS

    return NOT_SIGNED_IN


def sign_out_helper(token):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""DELETE FROM UserTokens WHERE token = ?""",
                                 (token,)).rowcount
            cur.close()
            g.db.commit()
        except sqlite3.Error:
            return False

        if status != 1:
            return False

    return True


def get_email_from_token(token):
    return get_email_from_token_helper(token)


def get_email_from_token_helper(token):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""SELECT email FROM UserTokens WHERE token = ?""",
                                 (token,)).fetchall()
            cur.close()
        except sqlite3.Error:
            return ""

    if status:
        return str(status[0][0])

    return ""


def change_password(token, old_password,
                    new_password):
    email = get_email_from_token(token)

    if email:
        if change_password_helper(email, old_password, new_password):
            return SUCCESS
        else:
            return WRONG_PASSWORD

    return NOT_SIGNED_IN


def change_password_helper(email, old_password, new_password):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""UPDATE Users SET password = ? WHERE email = ? AND password = ?""",
                                 (new_password, email, old_password,)).rowcount
            cur.close()
        except sqlite3.Error:
            return False

    if status != 1:
        return False

    return True


def get_user_data_by_token(token):
    return get_user_data_by_email(token, get_email_from_token(token))


def get_user_data_by_email(token, email):
    if email and email == get_email_from_token(token):
        unprocessed_data = get_user_data(email)

        if unprocessed_data:
            data = \
                {
                    'email': unprocessed_data[0],
                    'firstname': unprocessed_data[2],
                    'familyname': unprocessed_data[3],
                    'gender': unprocessed_data[4],
                    'city': unprocessed_data[5],
                    'country': unprocessed_data[6],
                }
            return SUCCESS, data

        return NO_SUCH_USER, None

    return NOT_SIGNED_IN, None


def get_user_data(email):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""SELECT * FROM Users WHERE email = ?""",
                                 (email,)).fetchall()
            cur.close()
        except sqlite3.Error:
            return ()

    if status:
        return status[0]

    return ()


def get_user_messages_by_token(token):
    return get_user_messages_by_email(token, get_email_from_token(token))


def get_user_messages_by_email(token, email):
    if get_email_from_token(token):
        if not user_exist(email):
            return NO_SUCH_USER, None

        messages = get_messages(email)
        data = [{"writer": writer, "message": message} for writer, message in messages]
        return SUCCESS, data

    return NOT_SIGNED_IN, None


def user_exist(email):
    with g.db:
        cur = g.db.cursor()
        try:
            cur.execute("""SELECT * FROM Users WHERE email = ?""", (email,))
            status = len(cur.fetchall())
            cur.close()
        except sqlite3.Error:
            return False

    if status != 1:
        return False

    return True


def get_messages(email):
    with g.db:
        cur = g.db.cursor()
        try:
            status = cur.execute("""SELECT Writer, Message FROM UserMessages WHERE email = ?""",
                                 (email,)).fetchall()
            cur.close()
        except sqlite3.Error:
            return ()

    if status:
        return status

    return ()


def post_message(token, message, email):
    if get_email_from_token(token):
        if not user_exist(email):
            return NO_SUCH_USER

        if post_message_helper(email, get_email_from_token(token), message):
            return SUCCESS

    return NOT_SIGNED_IN


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
