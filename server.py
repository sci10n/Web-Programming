import json
import random
import re

from flask import Flask, g, request
from flask.ext.bcrypt import Bcrypt
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import database_helper
from security import HashInfo, correct_hashed_data

app = Flask(__name__, static_url_path="")
bcrypt = Bcrypt(app)

SUCCESS = 1
NO_SUCH_USER = 2
NOT_SIGNED_IN = 3
WRONG_PASSWORD = 4
WRONG_USERNAME_PASSWORD = 5
USER_ALREADY_EXIST = 6
CORRUPT_DATA = 7
INVALID_DATA = 8

WEBSOCKETS = {}


@app.before_request
def before_request():
    g.db = database_helper.connect_db()


@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()


@app.route('/')
def home():
    return app.send_static_file("client.html")


@app.route('/signin/<client_hash>', methods=['POST'])
def sign_in_POST(client_hash):
    email = request.json['email']
    password = request.json['password']
    return json.dumps(sign_in(email, password,
                              HashInfo(route="signin",
                                       data=request.get_json(),
                                       hash=client_hash)))


@app.route('/signin/<token>')
def sign_in_token_POST(token):
    if request.environ.get("wsgi.websocket"):
        email = database_helper.get_email_from_token(token)
        if WEBSOCKETS.get(email):
            WEBSOCKETS[email].close()

        ws = request.environ.get("wsgi.websocket")
        WEBSOCKETS[email] = ws
        while ws.receive():
            pass

    return ""


@app.route('/signup/<client_hash>', methods=['POST'])
def sign_up_POST(client_hash):
    email = request.json['email']
    password = request.json['password']
    repassword = request.json['repassword']
    firstname = request.json['firstname']
    familyname = request.json['familyname']
    gender = request.json['gender']
    city = request.json['city']
    country = request.json['country']
    return json.dumps(sign_up(email, password, repassword,
                              firstname, familyname,
                              gender, city, country,
                              HashInfo(route="signup",
                                       data=request.get_json(),
                                       hash=client_hash)))


@app.route('/signout/<client_hash>', methods=['POST'])
def sign_out_POST(client_hash):
    token = request.json["token"]
    return json.dumps(sign_out(token,
                               HashInfo(route="signout",
                                        data=request.get_json(),
                                        hash=client_hash)))


@app.route('/changepassword/<client_hash>', methods=['POST'])
def change_password_POST(client_hash):
    token = request.json["token"]
    old_password = request.json["oldpassword"]
    new_password = request.json["newpassword"]
    return json.dumps(change_password(token, old_password, new_password,
                                      HashInfo(route="changepassword",
                                               data=request.get_json(),
                                               hash=client_hash)))


@app.route('/postmessage/<client_hash>', methods=['POST'])
def post_message_POST(client_hash):
    token = request.json["token"]
    message = request.json["message"]
    email = request.json["email"]
    return json.dumps(post_message(token, message, email,
                                   HashInfo(route="postmessage",
                                            data=request.get_json(),
                                            hash=client_hash)))


@app.route('/getuserdatabytoken/<token>/<client_hash>', methods=['GET'])
def get_user_data_by_token_GET(token, client_hash):
    return json.dumps(get_user_data_by_token(token,
                                             HashInfo(route="getuserdatabytoken",
                                                      hash=client_hash,
                                                      token=token)))


@app.route('/getuserdatabyemail/<token>/<email>/<client_hash>', methods=['GET'])
def get_user_data_by_email_GET(token, email, client_hash):
    return json.dumps(get_user_data_by_email(token, email,
                                             HashInfo(route="getuserdatabyemail",
                                                      hash=client_hash,
                                                      token=token,
                                                      email=email)))


@app.route('/getusermessagesbytoken/<token>/<client_hash>', methods=['GET'])
def get_user_messages_by_token_GET(token, client_hash):
    return json.dumps(get_user_messages_by_token(token,
                                                 HashInfo(route="getusermessagesbytoken",
                                                          hash=client_hash,
                                                          token=token)))


@app.route('/getusermessagesbyemail/<token>/<email>/<client_hash>', methods=['GET'])
def get_usr_messages_by_email_GET(token, email, client_hash):
    return json.dumps(get_user_messages_by_email(token, email,
                                                 HashInfo(route="getusermessagesbyemail",
                                                          hash=client_hash,
                                                          token=token,
                                                          email=email)))


def sign_in(email, password, hash_info):
    status, token = sign_in_helper(email, password, hash_info)

    if success(status):
        return {"success": True, "message": "Successfully signed in.", "data": token}

    return get_status_translation(status)


def sign_in_helper(email, password, hash_info):
    if not correct_hashed_data(hash_info):
        return CORRUPT_DATA, None

    if not correct_password(email, password):
        return WRONG_USERNAME_PASSWORD, None

    token = generate_token()
    while not database_helper.insert_token(email, token):
        token = generate_token()

    return SUCCESS, token


def correct_password(email, password):
    password_hash = database_helper.get_password_hash(email)

    if password_hash is None:
        return False

    return bcrypt.check_password_hash(password_hash, password)


def generate_token():
    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""

    for i in range(36):
        token += letters[random.randint(0, len(letters) - 1)]

    return token


def sign_up(email, password, repassword,
            firstname, familyname, gender, city,
            country, hash_info):
    if not correct_hashed_data(hash_info):
        return get_status_translation(CORRUPT_DATA)

    if not valid_email(email) or not valid_password(password) or \
            not matching_passwords(password, repassword):
        return get_status_translation(INVALID_DATA)

    password_hash = bcrypt.generate_password_hash(password)
    status = sign_up_helper(email=email, password=password_hash,
                            firstname=firstname, familyname=familyname,
                            gender=gender, city=city, country=country)

    if success(status):
        return {"success": True, "message": "Successfully created a new user."}

    return get_status_translation(status)


def sign_up_helper(email, password, firstname,
                   familyname, gender, city,
                   country):
    if database_helper.sign_up(email, password, firstname, familyname,
                               gender, city, country):
        return SUCCESS

    return USER_ALREADY_EXIST


def valid_email(email):
    return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)


def valid_password(password):
    return len(password) > 7


def matching_passwords(p1, p2):
    return p1 == p2


def sign_out(token, hash_info):
    status = sign_out_helper(token, hash_info)

    if success(status):
        return {"success": True, "message": "Successfully signed out."}

    return get_status_translation(status)


def sign_out_helper(token, hash_info):
    if not correct_hashed_data(hash_info):
        return CORRUPT_DATA

    email = database_helper.get_email_from_token(token)
    if database_helper.sign_out(token):
        WEBSOCKETS[email].close()
        return SUCCESS

    return NOT_SIGNED_IN


def change_password(token, old_password, new_password, hash_info):
    if not correct_hashed_data(hash_info):
        return get_status_translation(CORRUPT_DATA)

    if not valid_password(new_password):
        return get_status_translation(INVALID_DATA)

    status = change_password_helper(token, old_password, new_password)

    if success(status):
        return {"success": True, "message": "Password changed."}

    return get_status_translation(status)


def change_password_helper(token, old_password, new_password):
    email = database_helper.get_email_from_token(token)

    if email:
        if correct_password(email, old_password) and \
                database_helper.change_password(email,
                                                bcrypt.generate_password_hash(new_password)):
            return SUCCESS
        else:
            return WRONG_PASSWORD

    return NOT_SIGNED_IN


def get_user_data_by_token(token, hash_info):
    status, data = get_user_data_by_token_helper(token, hash_info)

    if success(status):
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_data_by_token_helper(token, hash_info):
    return get_user_data_by_email_helper(token, database_helper.get_email_from_token(token),
                                         hash_info)


def get_user_data_by_email(token, email, hash_info):
    status, data = get_user_data_by_email_helper(token, email, hash_info)

    if success(status):
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_data_by_email_helper(token, email, hash_info):
    if not correct_hashed_data(hash_info):
        return CORRUPT_DATA, None

    if user_exist(email):

        if user_exist(database_helper.get_email_from_token(token)):
            unprocessed_data = database_helper.get_user_data(email)

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

        return NOT_SIGNED_IN, None

    return NO_SUCH_USER, None


def get_user_messages_by_token(token, hash_info):
    status, data = get_user_messages_by_token_helper(token, hash_info)

    if success(status):
        return {"success": True, "message": "User messages retrieved.", "data": data}

    return get_status_translation(status)


def get_user_messages_by_token_helper(token, hash_info):
    return get_user_messages_by_email_helper(token, database_helper.get_email_from_token(token),
                                             hash_info)


def get_user_messages_by_email(token, email, hash_info):
    status, data = get_user_messages_by_email_helper(token, email, hash_info)

    if success(status):
        return {"success": True, "message": "User messages retrieved.", "data": data}

    return get_status_translation(status)


def get_user_messages_by_email_helper(token, email, hash_info):
    if not correct_hashed_data(hash_info):
        return CORRUPT_DATA, None

    if database_helper.get_email_from_token(token):
        if not user_exist(email):
            return NO_SUCH_USER, None

        messages = database_helper.get_messages(email)
        data = [{"writer": writer, "content": content} for writer, content in messages]
        return SUCCESS, data

    return NOT_SIGNED_IN, None


def user_exist(email):
    if database_helper.get_user_data(email):
        return True

    return False


def user_logged_in(email):
    if database_helper.get_token_from_email(email) is not None:
        return True

    return False


def post_message(token, message, email, hash_info):
    status = post_message_helper(token, message, email, hash_info)

    if success(status):
        return {"success": True, "message": "Message posted"}

    return get_status_translation(status)


def post_message_helper(token, message, email, hash_info):
    if not correct_hashed_data(hash_info):
        return CORRUPT_DATA

    if database_helper.get_email_from_token(token):
        if not user_exist(email):
            return NO_SUCH_USER

        if database_helper.post_message(email, database_helper.get_email_from_token(token), message):
            return SUCCESS

    return NOT_SIGNED_IN


def success(status):
    return status == SUCCESS


def get_status_translation(status):
    if status == NOT_SIGNED_IN:
        return {"success": False, "message": "You are not signed in."}
    elif status == NO_SUCH_USER:
        return {"success": False, "message": "No such user."}
    elif status == WRONG_PASSWORD:
        return {"success": False, "message": "Wrong password."}
    elif status == WRONG_USERNAME_PASSWORD:
        return {"success": False, "message": "Wrong username or password."}
    elif status == USER_ALREADY_EXIST:
        return {"success": False, "message": "User already exists."}
    elif status == CORRUPT_DATA:
        return {"success": False, "message": "Corrupt data."}
    elif status == INVALID_DATA:
        return {"success": False, "message": "Form data missing or incorrect type."}
    else:
        raise ValueError


if __name__ == "__main__":
    database_helper.init_db()
    app.debug = True
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
