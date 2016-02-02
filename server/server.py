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

@app.route("/user/<username>")
def create_user(username):
    with g.db:
        cur = g.db.cursor()
        cur.execute("INSERT INTO Users (Name) VALUES (?);", (username,))
        g.db.commit()

    return "CREATE_USER"

@app.route("/users")
def list_users():
    with g.db:
        cur = g.db.cursor()
        cur.execute("SELECT * FROM Users;")
        entries = [row[1] for row in cur.fetchall()]
        print(cur.fetchall())

    name_list = ""
    for name in entries:
        name_list += name + "\n"

    print(name_list)

    return name_list

def sign_in(email, password):
    raise NotImplementedError

def sign_up(email, password, firstname,
            familyname, gender, city,
            country):
    database_helper.sign_up(email=email, password=password,
                            firstname=firstname, familyname=familyname,
                            gender=gender, city=city, country=country)
    return "SIGN UP"

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

if __name__ == "__main__":
    database_helper.init_db()
    app.run(debug=True)