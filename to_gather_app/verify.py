import requests
from bs4 import BeautifulSoup

test_api = ""

def get_value(s,x):
    for input in s.find_all('input'):
        if input.get('name') == x :
            return input.get('value')

def try_ccnu(username = None, password = None):
    if (username is None) or (password is None):
        return False

    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36"
    }

    session = requests.Session()
    response = session.get('https://account.ccnu.edu.cn/cas/login', headers=headers)
    s = BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')
    lt = get_value(s, 'lt')
    exe = get_value(s, 'execution')
    payload={
        "username": username,
        "password": password,
        "lt":lt,
        "execution":exe,
        "_eventId":'submit',
        "submit":'登录'
    }
    r=session.post('https://account.ccnu.edu.cn/cas/login', data=payload)
    try:
        sc = r.headers['Set-Cookie']
    except:
        return False

    return True
