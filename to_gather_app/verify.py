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

    try:
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
        sc = r.headers.get('Set-Cookie') or ""
        if "CASTGC" in sc:
            return True
        else:
            return False
    except Exception as e:
        content = {
            "msgtype": "text",
            "text": {
                "content": "togather error" + str(e)
            }
        }
        headers = {
            'Content-Type':'application/json'
        }
        url = "https://oapi.dingtalk.com/robot/send?access_token=15f3493ae962cc45c1459c0655442b2f0c1d077565b3ebcbaf4bbfae6b21d649"
        r = requests.post(url, json=content, headers=headers)
        print(r.status_code)
        print(r.text)
        return False
