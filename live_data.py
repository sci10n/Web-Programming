import database_helper


class SignedUp(object):
    def __init__(self):
        self.signed_up = len(database_helper.signed_up_users())

    def json(self):
        return {"signedup": self.signed_up}


class SignedIn(object):
    def __init__(self):
        self.signed_in = len(database_helper.signed_in_users())

    def json(self):
        return {"signedin": self.signed_in}


class MaxMessages(object):
    def __init__(self):
        self.max_messages = max([len(database_helper.get_messages_by_email(user[0]))
                                 for user in database_helper.signed_up_users()])
        self.email = [user[0]
                      for user in database_helper.signed_up_users()
                      if len(database_helper.get_messages_by_email(user[0])) == self.max_messages]

    def json(self):
        return {"max_messages": self.max_messages}


class UserMessages(object):
    def __init__(self, email):
        self.user_messages = len(database_helper.get_messages_by_email(email))

    def json(self):
        return {"user_messages": self.user_messages}
