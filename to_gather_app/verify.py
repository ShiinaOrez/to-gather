import requests

test_api = ""

def try_ccnu(username = None, password = None):
    if (username is None) or (password is None):
        return False
    payload = {
        "username": username,
        "password": password
    }
