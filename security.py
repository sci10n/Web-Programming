import hashlib
import json


class HashInfo(object):
    def __init__(self, route, hash, data=None, token=None, email=None):
        self.route = route
        self.data = data
        self.hash = hash
        self.token = token
        self.email = email


def correct_hashed_data(hash_info):
    data_to_hash = "/" + hash_info.route

    if hash_info.token is not None:
        data_to_hash += "/" + hash_info.token

    if hash_info.email is not None:
        data_to_hash += "/" + hash_info.email

    if hash_info.data is not None:
        data_to_hash += "/" + json.dumps(hash_info.data,
                                         sort_keys=True,
                                         separators=(',', ':'))

    return hash_info.hash == hashlib.sha256(data_to_hash).hexdigest()
