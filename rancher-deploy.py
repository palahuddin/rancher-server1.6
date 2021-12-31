import requests, re, time
import os
from dotenv import load_dotenv
import json
import yaml


load_dotenv()


def compose_yaml():
    with open('docker-compose.yml','r') as file:
        data = file.read()
        compose_data = yaml.full_load(data)
        return (compose_data)

def rancher_yaml():
    with open('rancher-compose.yml','r') as file:
        data = file.read()
    rancher_data = yaml.full_load(data)
    return (rancher_data)

def read_json():
    x = compose_yaml()
    y = rancher_yaml()
    compose = str(x)
    rancher = str(y)
    if os.path.exists('deploy.json'):
        os.remove('deploy.json')
    data = {"dockerCompose": compose, "rancherCompose": rancher}
    with open('deploy.json','w') as deploy:
        json.dump(data, deploy)

def post_request():
    url = "https://"+os.getenv('RANCHER_URL')+"/v2-beta/projects/"+os.getenv('PROJECT_ID')+"/stacks/"+os.getenv('ID')+"?action=upgrade"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = open('deploy.json')
    url_call = requests.post(url, auth=(os.getenv('RANCHER_ACCESS_KEY'), os.getenv('RANCHER_SECRET_KEY')), headers=headers, data=payload)
    post_request.var = url_call.status_code
    res_text =  url_call.text
    return (payload)

def waiting_value():
    url = "https://"+os.getenv('RANCHER_URL')+"/v2-beta/projects/"+os.getenv('PROJECT_ID')+"/stacks/"+os.getenv('ID')
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    while True:
        url_call = requests.get(url, auth=(os.getenv('RANCHER_ACCESS_KEY'), os.getenv('RANCHER_SECRET_KEY')), headers=headers)
        res_text =  url_call.text
        in_dict = json.loads(res_text)
        result = in_dict['state']
        if result == "upgraded":
            print ('++++++++++++++++++++++++++++++++')
            time.sleep(5)
            print ('OK, Ready To', result)
            break
            return (result)
        else:
            print ('Wait Until Upgraded is Ready ...')
            time.sleep(5)

def finish_upgraded():
    url = "https://"+os.getenv('RANCHER_URL')+"/v2-beta/projects/"+os.getenv('PROJECT_ID')+"/stacks/"+os.getenv('ID')+"?action=finishupgrade"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    url_call = requests.post(url, auth=(os.getenv('RANCHER_ACCESS_KEY'), os.getenv('RANCHER_SECRET_KEY')), headers=headers)
    finish_upgraded.var = url_call.status_code
    res_text =  url_call.text
    return (res_text)        

# @app.route("/api")
def main():
    read_json()
    post_request()
    print ('Status Code',str(post_request.var))
    print ('++++++++++++++++++++++++++++++++')
    waiting_value()
    finish_upgraded()
    time.sleep(1)
    print ('Status Code',str(finish_upgraded.var))
    print ('')
    print ('')
    time.sleep(1)
    print ('Deployment Successfully....')

    
main()

