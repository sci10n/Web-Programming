import re
import random

import database_helper

from flask import Flask, g

app = Flask(__name__)

@app.before_request
def before_request():
    g.db = database_helper.connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, "gb"):
        g.db.close()

@app.route("/")
def home():
    return "OMG"

@app.route("/debug/signup")
def debug_sign_up():
    email = "asd@asd.com"
    password = "asdasdasd"
    firstname = "asdasd"
    familyname = "asd"
    gender = "asd"
    city = "asd"
    country = "asd"

    print(sign_up(email, password, firstname, familyname, gender, city, country))

    return "SIGN UP"

@app.route("/debug/signin")
def debug_sign_in():
    email = "asd@asd.com"
    password = "asdasdasd"

    print(sign_in(email, password))

    return "SIGN IN"

@app.route("/debug/signout")
def debug_sign_out():
     token = "aaa"

     print(sign_out(token))

     return "SIGN OUT"

@app.route("/debug/changepw")
def debug_change_password():
     token = "aaa"
     old_password = "asdasdasd"
     new_password = "asdasdasdasd"

     print(change_password(token, old_password, new_password))

     return "SIGN OUT"

@app.route("/debug/pm")
def debug_post_message():
     token = "aaa"
     message = "HELLO WORLD"
     email = "asd@asd.com"

     print(post_message(token, message, email))

     return "SIGN OUT"

@app.route("/debug/gm")
def debug_get_message():
     token = "aaa"
     email = "asd@asd.com"

     print(get_user_messages_by_token(token))

     return "SIGN OUT"

def generate_token():
    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""

    for i in range(36):
        token += letters[random.randint(0, len(letters) - 1)]

    return "aaa"

def sign_in(email, password):
    if database_helper.sign_in(email, password):
        token = generate_token()
        while not database_helper.insert_token(email, token):
            token = generate_token()
        return {"success": True, "message": "Successfully signed in.", "data": token}
    return {"success": False, "message": "Wrong username or password."}

def valid_email(email):
    return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)

def valid_password(password):
    return len(password) > 7

def sign_up(email, password, firstname,
            familyname, gender, city,
            country):

    if not valid_email(email) or not valid_password(password):
        return {"success": False, "message": "Form data missing or incorrect type."}

    if database_helper.sign_up(email=email, password=password,
                            firstname=firstname, familyname=familyname,
                            gender=gender, city=city, country=country):
        return {"success": True, "message": "Successfully created a new user."}

    return {"success": False, "message": "User already exists."}

def sign_out(token):
    if database_helper.sign_out(token):
        return {"success": True, "message": "Successfully signed out."}

    return {"success": False, "message": "You are not signed in."}

def change_password(token, old_password,
                    new_password):

    status = database_helper.change_password(token, old_password, new_password)

    if status == 1:
        return {"success": True, "message": "Password changed."}
    elif status == 2:
        return {"success": False, "message": "Wrong password."}
    elif status == 3:
        return {"success": False, "message": "You are not logged in."}

def get_user_data_by_token(token):
    return database_helper.get_user_data_by_token(token)

def get_user_data_by_email(token, email):
    return database_helper.get_user_data_by_email(token, email)

def get_user_messages_by_token(token):
    return database_helper.get_user_messages_by_token(token)

def get_user_messages_by_email(token, email):
    return database_helper.get_user_messages_by_email(token, email)

def post_message(token, message, email):
    return database_helper.post_message(token, message, email)

if __name__ == "__main__":
    database_helper.init_db()
    app.run(debug=True)