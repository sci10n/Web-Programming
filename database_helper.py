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
    if hasattr(g, "gb"):
        g.db.close()


def get_password_hash(email):
    result = execute_query("""SELECT * FROM Users WHERE email = ?""",
                           [email])

    if result:
        return result[0][1]

    return None


def get_token_from_email(email):
    result = execute_query("""SELECT * FROM UserTokens WHERE email = ?""",
                           [email])

    if result:
        return result[0][1]

    return None


def insert_token(email, token):
    result = execute_query("""INSERT INTO UserTokens (email, token)
                              VALUES (?, ?)""",
                           [email, token], commit=True)

    if result == 1:
        return True

    return False


def sign_up(email, password, firstname,
            familyname, gender, city, country):
    result = execute_query("""INSERT INTO Users (email, password, firstname, familyname, gender, city, country)
                              VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           [email, password, firstname, familyname, gender, city, country], commit=True)

    if result == 1:
        return True

    return False


def sign_out(token):
    result = execute_query("""DELETE FROM UserTokens WHERE token = ?""",
                           [token], commit=True)

    print(token, result)

    if result == 1:
        return True

    return False


def get_email_from_token(token):
    result = execute_query("""SELECT email FROM UserTokens WHERE token = ?""",
                           [token])

    if result:
        return str(result[0][0])

    return ""


def change_password(email, new_password):
    result = execute_query("""UPDATE Users SET password = ? WHERE email = ?""",
                           [new_password, email], commit=True)

    if result == 1:
        return True

    return False


def get_user_data(email):
    result = execute_query("""SELECT * FROM Users WHERE email = ?""",
                           [email])

    if result:
        return result[0]

    return ()


def get_messages_by_email(email):
    result = execute_query("""SELECT Writer, Message FROM UserMessages WHERE email = ?""",
                           [email])

    if result:
        return result

    return ()


def get_messages():
    result = execute_query("""SELECT Writer, Message FROM UserMessages""")

    if result:
        return result

    return ()


def post_message(email, writer, message):
    result = execute_query("""INSERT INTO UserMessages (email, writer, message)
                           VALUES (?, ?, ?)""",
                           [email, writer, message], commit=True)
    if result == 1:
        return True

    return False


def signed_up_users():
    result = execute_query("""SELECT * FROM Users""")

    if result:
        return result

    return ()


def signed_in_users():
    result = execute_query("""SELECT * FROM UserTokens""")

    if result:
        return result

    return ()


def execute_query(query, args=(), commit=False):
    with g.db:
        cur = g.db.cursor()
        try:
            result = cur.execute(query, args).fetchall()

            if commit:
                result = cur.rowcount
                g.db.commit()

            cur.close()

        except sqlite3.Error:
            return None

    return result
