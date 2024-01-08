import requests
import datetime
import base64
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage


TOKEN_FILE_PATH = '/data/token.json'
CREDENTIALS_FILE_PATH = '/data/credentials.json'
DISNEYTOKEN_PATH = '/data/disneyToken.json'

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']


def main():
    # service = get_gmail_service()
    # gmail_send_message(service, "example@example.com", "Test", "Testing gmail api")

    pass


def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE_PATH, "w") as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def gmail_send_message(service, to, subject, content):
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id
  """
  try:
    message = EmailMessage()

    message.set_content(content)

    message["To"] = to
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message


# Function to load klas data from JSON file
def load_disney_token():
    if os.path.exists(DISNEYTOKEN_PATH):
        with open(DISNEYTOKEN_PATH, "r") as f:
            return json.load(f)['auth_token']
    else:
        return {}
    

# Function to save klas data to JSON file
def save_disney_token(data):
    with open(DISNEYTOKEN_PATH, "w") as f:
        json.dump(data, f, indent=4)


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


def checkTable(tableUrl, auth_key, date, partysize):
    payload = {
        'date': date,
        'partyMix': partysize,
        # 'restaurantId': restaurantId,
        'session': 3 # Without this an empty list is returned.
    }
    
    headers = {
        'User-Agent': '',
        'Authorization': f'Bearer {auth_key}',
        'x-api-key': os.environ['API_KEY']
    }

    json_payload = json.dumps(payload)

    # printDated(f"Sending request {json_payload}")
    x = requests.post(tableUrl, headers=headers, data=json_payload)

    if x.status_code != 200:
        printDated(x.status_code)
        return False

    json_response = json.loads(x.text)

    try:
        availability = json_response[0]
    except KeyError:
        try:
            printDated(f"{json_response['status']}: {json_response['error']}")
        except:
            if 'BAD_AUTHZ_TOKEN' in json_response:
                print("Refreshing auth token")
                refresh_disney_token(os.environ['DISNEY_USERNAME'], os.environ['DISNEY_PASSWORD'], load_disney_token())
        return False
    except IndexError:
        printDated(f"IndexError: {json_response}")
        return False
    
    # Check for open spots in returned restaurant data
    availableRestaurantIds = set()
    for availability in json_response:
        for mealPeriod in availability['mealPeriods']:
            for slot in mealPeriod['slotList']:
                if slot['available'] == 'true':
                    availableRestaurantIds.add(availability['restaurantId'])

    return availableRestaurantIds


def load_data(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        printDated(f"Could not find file {path}")
        return {}


def printDated(message):
    now = datetime.datetime.today().replace(microsecond=0)
    print(f"{now.isoformat()}: {message}")


if __name__ == "__main__":
    main()