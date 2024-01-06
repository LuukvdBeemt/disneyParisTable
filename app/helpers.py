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

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']


def main():
    checkTable('2024-01-11', 2)
    # service = get_gmail_service()
    # gmail_send_message(service, "example@example.com", "Test", "Testing gmail api")


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


def checkTable(tableUrl, auth_key, date, partysize):

    payload = {
        'date': date,
        'partyMix': partysize,
        # 'restaurantId': restaurantId,
        'session': 3 # Without this an empty list is returned.
    }
    
    headers = {
        'User-Agent': '',
        'Authorization': auth_key,
        'x-api-key': os.environ['API_KEY']
    }

    json_payload = json.dumps(payload)

    # printDated(f"Sending request {json_payload}")
    x = requests.post(tableUrl, headers=headers, data=json_payload)

    if x.status_code != 200:
        printDated(x.status_code)
        return False

    json_response = json.loads(x.text)

    # if 'status' in json_response.keys():
    #     if json_response['status'] == 429:
    #         printDated(json_response['status'])
    #         return False

    try:
        availability = json_response[0]
    except KeyError:
        try:
            printDated(f"{json_response['status']}: {json_response['error']}")
        except:
            print(json_response)
        return False
    except IndexError:
        printDated(f"IndexError: {json_response}")
        return False
    
    # availableSlots = []
    availableRestaurantIds = set()
    for availability in json_response:
        for mealPeriod in availability['mealPeriods']:
            for slot in mealPeriod['slotList']:
                if slot['available'] == 'true':
                    # availableSlots.append(slot)
                    availableRestaurantIds.add(availability['restaurantId'])

    # printDated(availableRestaurantIds)
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