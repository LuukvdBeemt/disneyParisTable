import os
import json
import requests

from helpers import load_disney_token, save_disney_token, printDated


def main():
    refresh_disney_token(os.environ.get['DISNEY_USERNAME'], os.environ.get['DISNEY_PASSWORD'], load_disney_token())


def refresh_disney_token(username, password, old_auth_key):
    loginUrl = 'https://registerdisney.go.com/jgc/v8/client/TPR-DLP.WEB-PROD/guest/reauth'
    payload = {
        'loginValue': username,
        'password': password
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Authorization': f'Bearer {old_auth_key}',
        'content-type': 'application/json'
    }

    json_payload = json.dumps(payload)

    x = requests.post(loginUrl, headers=headers, data=json_payload)

    json_response = json.loads(x.text)

    try:
        new_auth_token = json_response['data']['token']['access_token']
    except TypeError:
        printDated("Could not refresh token: ")
        print(json_response)

    data = {
        'auth_token': new_auth_token
    }
    save_disney_token(data)
    printDated("Token succesfully refreshed")

    return new_auth_token


if __name__ == "__main__":
    main()