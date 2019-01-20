from datetime import datetime
import time

# CONSOLE LOG
cfromat = "[{time}] {spaсe_level}{msg}"
def print_message(message, level=0, end=None):
    level_indent = " " * level
    try:
        print(
            cfromat.format(
                time=datetime.now(),
                spaсe_level=level_indent,
                msg=message),
            end=end)
    except BaseException:
        print(
            cfromat.format(
                time=datetime.now(),
                spaсe_level=level_indent,
                msg="Message can not be displayed because the encoding is not supported."))
#

def read_token(source):
    if source == 'tlg':
        with open('token.ctl', 'r') as f:
            token = f.readline()
    if source == 'vk':
        with open('vk_token.ctl', 'r') as f:
            token = f.readline()
    return token

def read_token_twitter():
    with open('tw_token.ctl', 'r') as f:
        tokens = f.readlines()
        APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET = [t.strip() for t in tokens]
    return APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

def read_login_pwd():
    with open('login_pwd.pwd', 'r') as f:
        login, pwd = f.readline().split(':')
    return login, pwd

def read_tlg_token():
    with open('tlg_client_token.ctl', 'r') as fin:
        line = fin.readline()
        api_id, api_hash, phone = line.split(',')
    return api_id, api_hash, phone