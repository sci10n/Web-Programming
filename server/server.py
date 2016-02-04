import re

from flask import Flask, g

import database_helper

app = Flask(__name__)


@app.before_request
def before_request():
    g.db = database_helper.connect_db()


@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()


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

    return "POST MESSAGE"


@app.route("/debug/gm")
def debug_get_message():
    token = "aaa"
    email = "asd@asd.com"

    print(get_user_messages_by_token(token))

    return "GET MESSAGE"


def sign_in(email, password):
    status, token = database_helper.sign_in(email, password)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "Successfully signed in.", "data": token}

    return get_status_translation(status)


def sign_up(email, password, firstname,
            familyname, gender, city,
            country):
    if not valid_email(email) or not valid_password(password):
        return {"success": False, "message": "Form data missing or incorrect type."}

    status = database_helper.sign_up(email=email, password=password,
                                     firstname=firstname, familyname=familyname,
                                     gender=gender, city=city, country=country)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "Successfully created a new user."}

    return get_status_translation(status)


def valid_email(email):
    return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)


def valid_password(password):
    return len(password) > 7


def sign_out(token):
    status = database_helper.sign_out(token)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "Successfully signed out."}

    return get_status_translation(status)


def change_password(token, old_password,
                    new_password):
    status = database_helper.change_password(token, old_password, new_password)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "Password changed."}

    return get_status_translation(status)


def get_user_data_by_token(token):
    status, data = database_helper.get_user_data_by_token(token)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_data_by_email(token, email):
    status, data = database_helper.get_user_data_by_email(token, email)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_messages_by_token(token):
    status, data = database_helper.get_user_messages_by_token(token)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "User messages retrieved.", "data": data}

    return get_status_translation(status)


def get_user_messages_by_email(token, email):
    status, data = get_user_messages_by_email(token, email)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "User messages retrieved.", "data": data}

    return get_status_translation(status)


def post_message(token, message, email):
    status = database_helper.post_message(token, message, email)

    if status == database_helper.SUCCESS:
        return {"success": True, "message": "Message posted"}

    return get_status_translation(status)


def get_status_translation(status):
    if status == database_helper.NOT_SIGNED_IN:
        return {"success": False, "message": "You are not signed in."}
    elif status == database_helper.NO_SUCH_USER:
        return {"success": False, "message": "No such user."}
    elif status == database_helper.WRONG_PASSWORD:
        return {"success": False, "message": "Wrong password."}
    elif status == database_helper.WRONG_USERNAME_PASSWORD:
        return {"success": False, "message": "Wrong username or password."}
    elif status == database_helper.USER_ALREADY_EXIST:
        return {"success": False, "message": "User already exists."}
    else:
        raise ValueError


if __name__ == "__main__":
    database_helper.init_db()
    app.run(debug=True)
