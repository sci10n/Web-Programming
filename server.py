import json
import random
import re
from datetime import datetime

from flask import Flask, g, request
from flask.ext.bcrypt import Bcrypt
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import database_helper
from live_data import MaxMessages, UserMessages, SignedUp, SignedIn
from security import HashInfo, correct_hash

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
INVALID_TIMESTAMP = 9

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


@app.route('/signin/', methods=['POST'])
def sign_in_POST():
    email = request.json['email']
    password = request.json['password']
    timestamp = request.json["timestamp"]
    return json.dumps(sign_in(email, password, timestamp))


@app.route('/signin/<email>/<timestamp>/<client_hash>')
def sign_in_token_POST(email, timestamp, client_hash):
    token = database_helper.get_token_from_email(email)
    if not correct_hash(HashInfo(route="signin",
                                 token=token,
                                 data={"email": email,
                                       "timestamp": int(timestamp)},
                                 hash=client_hash)) or \
            not valid_timestamp(int(timestamp)):
        database_helper.sign_out(token)
        return ""

    if request.environ.get("wsgi.websocket"):
        ws = request.environ.get("wsgi.websocket")

        WEBSOCKETS[email] = ws

        send_all_data_to_email(email)
        send_signed_in_to_all()

        while ws.receive():
            pass

    database_helper.sign_out(token)
    return ""


@app.route('/signup/', methods=['POST'])
def sign_up_POST():
    email = request.json['email']
    password = request.json['password']
    repassword = request.json['repassword']
    firstname = request.json['firstname']
    familyname = request.json['familyname']
    gender = request.json['gender']
    city = request.json['city']
    country = request.json['country']
    timestamp = request.json["timestamp"]
    return json.dumps(sign_up(email, password, repassword,
                              firstname, familyname,
                              gender, city, country,
                              timestamp))


@app.route('/signout/', methods=['POST'])
def sign_out_POST():
    token = database_helper.get_token_from_email(request.json["email"])
    timestamp = request.json["timestamp"]
    client_hash = request.json['hash']
    data = {"token": token,
            "timestamp": timestamp}
    return json.dumps(sign_out(token, timestamp,
                               HashInfo(route="signout",
                                        data=data,
                                        hash=client_hash)))


@app.route('/changepassword/', methods=['POST'])
def change_password_POST():
    token = database_helper.get_token_from_email(request.json["email"])
    old_password = request.json["oldpassword"]
    new_password = request.json["newpassword"]
    client_hash = request.json['hash']
    timestamp = request.json["timestamp"]
    data = {"newpassword": new_password,
            "oldpassword": old_password,
            "token": token,
            "timestamp": timestamp}
    return json.dumps(change_password(token, old_password, new_password, timestamp,
                                      HashInfo(route="changepassword",
                                               data=data,
                                               hash=client_hash)))


@app.route('/postmessage/', methods=['POST'])
def post_message_POST():
    client_email = request.json["client_email"]
    token = database_helper.get_token_from_email(client_email)
    message = request.json["message"]
    post_email = request.json["post_email"]
    client_hash = request.json['hash']
    timestamp = request.json["timestamp"]
    data = {"client_email": client_email,
            "message": message,
            "post_email": post_email,
            "timestamp": timestamp,
            "token": token}
    return json.dumps(post_message(token, message,
                                   post_email, timestamp,
                                   HashInfo(route="postmessage",
                                            data=data,
                                            hash=client_hash)))


@app.route('/getuserdatabytoken/<email>/<client_hash>', methods=['GET'])
def get_user_data_by_token_GET(email, client_hash):
    token = database_helper.get_token_from_email(email)
    return json.dumps(get_user_data_by_token(token,
                                             HashInfo(route="getuserdatabytoken",
                                                      hash=client_hash,
                                                      token=token)))


@app.route('/getuserdatabyemail/<client_email>/<email>/<client_hash>', methods=['GET'])
def get_user_data_by_email_GET(client_email, email, client_hash):
    token = database_helper.get_token_from_email(client_email)
    return json.dumps(get_user_data_by_email(token, email,
                                             HashInfo(route="getuserdatabyemail",
                                                      hash=client_hash,
                                                      token=token,
                                                      email=email)))


@app.route('/getusermessagesbytoken/<email>/<client_hash>', methods=['GET'])
def get_user_messages_by_token_GET(email, client_hash):
    token = database_helper.get_token_from_email(email)
    return json.dumps(get_user_messages_by_token(token,
                                                 HashInfo(route="getusermessagesbytoken",
                                                          hash=client_hash,
                                                          token=token)))


@app.route('/getusermessagesbyemail/<client_email>/<email>/<client_hash>', methods=['GET'])
def get_usr_messages_by_email_GET(client_email, email, client_hash):
    token = database_helper.get_token_from_email(client_email)
    return json.dumps(get_user_messages_by_email(token, email,
                                                 HashInfo(route="getusermessagesbyemail",
                                                          hash=client_hash,
                                                          token=token,
                                                          email=email)))


def sign_in(email, password, timestamp):
    status, token = sign_in_helper(email=email,
                                   password=password,
                                   timestamp=timestamp)

    if success(status):
        if WEBSOCKETS.get(email, False):
            WEBSOCKETS[email].close()

        return {"success": True, "message": "Successfully signed in.", "data": token}

    return get_status_translation(status)


def sign_in_helper(email, password, timestamp):
    if not valid_timestamp(timestamp):
        return INVALID_TIMESTAMP, None

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
            country, timestamp):
    if not valid_timestamp(timestamp):
        return get_status_translation(INVALID_TIMESTAMP)

    if not valid_email(email) or not valid_password(password) or \
            not matching_passwords(password, repassword):
        return get_status_translation(INVALID_DATA)

    password_hash = bcrypt.generate_password_hash(password)
    status = sign_up_helper(email=email, password=password_hash,
                            firstname=firstname, familyname=familyname,
                            gender=gender, city=city, country=country)

    if success(status):
        send_signed_up_to_all()
        return {"success": True, "message": "Successfully created a new user."}

    return get_status_translation(status)


def sign_up_helper(email, password, firstname,
                   familyname, gender, city,
                   country):
    if database_helper.sign_up(email=email, password=password,
                               firstname=firstname, familyname=familyname,
                               gender=gender, city=city, country=country):
        return SUCCESS

    return USER_ALREADY_EXIST


def valid_email(email):
    return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)


def valid_password(password):
    return len(password) > 7


def matching_passwords(p1, p2):
    return p1 == p2


def sign_out(token, timestamp, hash_info):
    status = sign_out_helper(token, timestamp, hash_info)

    if success(status):
        send_signed_in_to_all()
        return {"success": True, "message": "Successfully signed out."}

    return get_status_translation(status)


def sign_out_helper(token, timestamp, hash_info):
    if not valid_timestamp(timestamp):
        return INVALID_TIMESTAMP

    if not correct_hash(hash_info):
        return CORRUPT_DATA

    email = database_helper.get_email_from_token(token)
    if database_helper.sign_out(token):
        if WEBSOCKETS.get(email, False):
            WEBSOCKETS[email].close()
        return SUCCESS

    return NOT_SIGNED_IN


def change_password(token, old_password, new_password,
                    timestamp, hash_info):
    if not correct_hash(hash_info):
        return get_status_translation(CORRUPT_DATA)

    if not valid_timestamp(timestamp):
        return get_status_translation(INVALID_TIMESTAMP)

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
    status, data = get_user_data_by_token_helper(token=token,
                                                 hash_info=hash_info)

    if success(status):
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_data_by_token_helper(token, hash_info):
    return get_user_data_by_email_helper(token,
                                         database_helper.get_email_from_token(token),
                                         hash_info)


def get_user_data_by_email(token, email, hash_info):
    status, data = get_user_data_by_email_helper(token=token,
                                                 email=email,
                                                 hash_info=hash_info)

    if success(status):
        return {"success": True, "message": "User data retrieved.", "data": data}

    return get_status_translation(status)


def get_user_data_by_email_helper(token, email, hash_info):
    if not correct_hash(hash_info):
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
    if not correct_hash(hash_info):
        return CORRUPT_DATA, None

    if database_helper.get_email_from_token(token):
        if not user_exist(email):
            return NO_SUCH_USER, None

        messages = database_helper.get_messages_by_email(email)
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


def valid_timestamp(timestamp):
    max_minutes = 5
    max_seconds = max_minutes * 60

    t = datetime.fromtimestamp(timestamp / 1000.0)
    dt = datetime.now() - t

    if dt.total_seconds() > max_seconds or dt.total_seconds() < 0:
        return False

    return True


def post_message(token, message, email, timestamp, hash_info):
    status = post_message_helper(token=token,
                                 message=message,
                                 email=email,
                                 timestamp=timestamp,
                                 hash_info=hash_info)

    if success(status):
        send_user_messages_to_email(email)
        max_messages = MaxMessages()
        if email in max_messages.emails and len(max_messages.emails) == 1:
            send_max_messages_to_all()

        return {"success": True, "message": "Message posted"}

    return get_status_translation(status)


def post_message_helper(token, message, email,
                        timestamp, hash_info):
    if not correct_hash(hash_info):
        return CORRUPT_DATA

    if not valid_timestamp(timestamp):
        return INVALID_TIMESTAMP

    if database_helper.get_email_from_token(token):
        if not user_exist(email):
            return NO_SUCH_USER

        if database_helper.post_message(email,
                                        database_helper.get_email_from_token(token),
                                        message):
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
    elif status == INVALID_TIMESTAMP:
        return {"success": False, "message": "Invalid timestamp."}
    else:
        raise ValueError


def send_user_messages_to_email(email):
    if WEBSOCKETS.get(email, False):
        WEBSOCKETS[email].send(json.dumps(UserMessages(email).json()))


def send_max_messages_to_all():
    send_data_to_all(MaxMessages().json())


def send_signed_up_to_all():
    send_data_to_all(SignedUp().json())


def send_signed_in_to_all():
    send_data_to_all(SignedIn().json())


def send_all_data_to_email(email):
    all_data = {}
    all_data.update(UserMessages(email).json())
    all_data.update(MaxMessages().json())
    all_data.update(SignedIn().json())
    all_data.update(SignedUp().json())

    if WEBSOCKETS.get(email, False):
        WEBSOCKETS[email].send(json.dumps(all_data))


def send_data_to_all(data):
    for email, _ in database_helper.signed_in_users():
        if WEBSOCKETS.get(email, False):
            WEBSOCKETS[email].send(json.dumps(data))


if __name__ == "__main__":
    database_helper.init_db()
    app.debug = True
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
