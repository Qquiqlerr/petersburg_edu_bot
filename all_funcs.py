import json
import lxml
import prettytable
from prettytable import PrettyTable
import requests.cookies
import os
from bs4 import BeautifulSoup
import ast
url = 'https://dnevnik2.petersburgedu.ru/api/user/auth/login'
user = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
header = {
    'User-Agent':user
}
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

list_period = {
    'first_half' : {
        'id' : 81811,
        'estimate_type' : 30
    },
    'second_half' : {
        'id' : 81942,
        'estimate_type' : 31
    },
    'year' : {
        'id' : 81805,
        'estimate_type' : 32
    }
}

def json_loads_from_path(path):
    conf_path = os.path.join(ROOT_DIR, f'{path}')
    with open(f'{conf_path}','r') as f:
        js = json.load(f)
    return js

def create_data(log_and_pass):
    login,password = log_and_pass.split(':')
    datas = {
        'login': login,
        'password': password,
        'type': 'email'
    }
    return datas

def set_eduID(session,period):
    s = json_loads_from_path('headers.json')
    cldId = json.loads(session.get('https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list?p_page=1', headers=s).content)['data']['items'][0]['educations'][0]['education_id']
    print(cldId)
    param = {
        'p_educations[]': cldId,
        'p_estimate_types[]': list_period[f'{period}']['estimate_type'],
        'p_page' : 1,
        'p_periods[]': list_period[f'{period}']['id']
    }
    return param
def make_cookies_with_json(cookies,user_id):
    ccs = json.loads(cookies)['data']['token']
    if not os.path.isdir(f"User_info/{user_id}"):
        os.mkdir(f"User_info/{user_id}")
    conf_path = os.path.join(ROOT_DIR, f"User_info/{user_id}/cookies.json")
    with open(conf_path,'w') as f:
        json.dump([
              {
                "name": "X-JWT-Token",
                "value": f'{ccs}',
                "domain": "dnevnik2.petersburgedu.ru",
                "path": "/",
                "expires": None
              }
            ],f)
def auth_and_create_cookies(datas,user_id):
    session = requests.Session()
    s = json_loads_from_path('headers.json')
    logging = session.post(url, json=datas, headers=s)

    cookie = json.loads(logging.content)
    session.close()
    return make_cookies_with_json(logging.content,user_id)



def create_session(user_id):
    session = requests.session()
    cookies = json_loads_from_path(f'User_info/{user_id}/cookies.json')
    session = requests.Session()
    s = json_loads_from_path('headers.json')
    cookies_jar = requests.cookies.RequestsCookieJar()
    for item in cookies:
        cookies_jar.set(**item)
    session.cookies.update(cookies_jar)
    return session

def get_marks(user_id,period):
    output = PrettyTable(['Предмет','Оценка'])
    output.set_style(prettytable.MARKDOWN)
    output.align = 'l'
    output.hrules = prettytable.ALL
    output.vrules = prettytable.NONE
    session = create_session(user_id)
    param = set_eduID(session,period)
    profile = session.post('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', headers=header, params=param)
    #print(profile.text)
    soup = BeautifulSoup(profile.content, "lxml").find('p').contents[0]
    subject_name = ''
    estimate_value_name = ''
    print(soup)
    jssoup = json.loads(soup)
    for i in range(len(jssoup['data']['items'])):
        for key, value in jssoup['data']['items'][i].items():
            if key == 'subject_name':
                subject_name = value
            elif key == 'estimate_value_name':
                estimate_value_name = value
            tmp = "\n".join(subject_name.split())
        output.add_row([tmp,estimate_value_name])
        subject_name = ''
        estimate_value_name = ''
    session.close()
    return output
def set_eduID_for_curmarks(session):
    s = json_loads_from_path('headers.json')
    cldId = json.loads(session.get('https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list?p_page=1', headers=s).content)['data']['items'][0]['educations'][0]['education_id']
    param = {
        'p_educations[]': cldId,
        'p_date_from:' : '09.01.2023',
        'p_date_to:' : '31.05.2023',
        'p_page' : 1,
        'p_limit' : 100
    }
    return param
def get_current_marks(user_id):
    codes = [
        1063,
        1058,
        11204,
        1065,
        1077,
        1092
    ]
    output = PrettyTable(['Предмет', 'Оценки'])
    output.set_style(prettytable.MARKDOWN)
    output.align = 'l'
    output.hrules = prettytable.ALL
    output.vrules = prettytable.NONE

    session = create_session(user_id)
    param = set_eduID_for_curmarks(session)
    output_dict = {}
    profile = session.post('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', headers=header, params=param)
    soup = BeautifulSoup(profile.content, "lxml").find('p').contents[0]
    jssoup = json.loads(soup)
    print(jssoup)
    for i in jssoup['data']['items']:
        print(i)
        print(i['estimate_type_code'])
        if int(i['estimate_type_code']) in codes:

            output_dict[i['subject_name']] = output_dict.get(i['subject_name'], []) + [i['estimate_value_name']]
    print(output_dict)
    for key,value in output_dict.items():
        output.add_row([key, value])
    return output
print(get_current_marks(481370222))
