import json
import re

from flask import Flask, g, request

import database_helper

app = Flask(__name__)


@app.before_request
def before_request():
    g.db = database_helper.connect_db()


@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()


@app.route('/signin', methods=['POST'])
def sign_in_POST():
    email = request.form['email']
    password = request.form['password']
    return json.dumps(sign_in(email, password))


@app.route('/signup', methods=['POST'])
def sign_up_POST():
    email = request.form['email']
    password = request.form['password']
    firstname = request.form['firstname']
    familyname = request.form['familyname']
    gender = request.form['gender']
    city = request.form['city']
    country = request.form['country']
    return json.dumps(sign_up(email, password, firstname, familyname,
                              gender, city, country))

@app.route('/signout', methods=['POST'])
def sign_out_POST():
    token = request.form["token"]
    return json.dumps(sign_out(token))


@app.route('/changepw', methods=['POST'])
def change_pw_POST():
    token = request.form["token"]
    old_password = request.form["oldpassword"]
    new_password = request.form["newpassword"]
    return json.dumps(change_password(token, old_password, new_password))


@app.route('/postmsg', methods=['POST'])
def post_msg_POST():
    token = request.form["token"]
    message = request.form["message"]
    email = request.form["email"]
    return json.dumps(post_message(token, message, email))


@app.route('/getuserdatabytoken/<token>', methods=['GET'])
def get_usr_data_by_token_GET(token):
    return json.dumps(get_user_data_by_token(token))


@app.route('/getuserdatabyemail/<token>/<email>', methods=['GET'])
def get_usr_data_by_email_GET(token, email):
    return json.dumps(get_user_data_by_email(token, email))


@app.route('/getusermessagesbytoken/<token>', methods=['GET'])
def get_usr_messages_by_token_GET(token):
    return json.dumps(get_user_messages_by_token(token))


@app.route('/getusermessagesbyemail/<token>/<email>', methods=['GET'])
def get_usr_messages_by_email_GET(token, email):
    return json.dumps(get_user_messages_by_email(token, email))


def sign_in(email, password):
    status, token = database_helper.sign_in(email, password)

    if success(status):
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

    if success(status):
        return {"success": True, "message": "Successfully created a new user."}

    return get_status_translation(status)


def valid_email(email):
    return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)


def valid_password(password):
    return len(password) > 7


def sign_out(token):
    status = database_helper.sign_out(token)

    if success(status):
        return {"success": True, "message": "Successfully signed out."}

    return get_status_translation(status)


def change_password(token, old_password, new_password):
    if not valid_password(new_password):
        return {"success": False, "message": "Form data missing or incorrect type."}

    status = database_helper.change_password(token, old_password, new_password)

    if success(status):
        return {"success": True, "message": "Password changed."}

    return get_status_translation(status)


def get_user_data_by_token(token):
    status, data = database_helper.get_user_data_by_token(token)

    if success(status):
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_data_by_email(token, email):
    status, data = database_helper.get_user_data_by_email(token, email)

    if success(status):
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_messages_by_token(token):
    status, data = database_helper.get_user_messages_by_token(token)

    if success(status):
        return {"success": True, "message": "User messages retrieved.", "data": data}

    return get_status_translation(status)


def get_user_messages_by_email(token, email):
    status, data = get_user_messages_by_email(token, email)

    if success(status):
        return {"success": True, "message": "User messages retrieved.", "data": data}

    return get_status_translation(status)


def post_message(token, message, email):
    status = database_helper.post_message(token, message, email)

    if success(status):
        return {"success": True, "message": "Message posted"}

    return get_status_translation(status)


def success(status):
    return status == database_helper.SUCCESS


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
