import base64
import os
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from text_json import process_pdf
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
JSON = os.getenv('GOOGLE_SECRET_JSON')
TOKEN_PATH = os.getenv('TOKEN_PATH')
USER_ID = 'me'
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
TOPIC_NAME = os.getenv('TOPIC_NAME')

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def build_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def subscribe_to_gmail(user_id, topic_name, webhook_url):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)  # Use your existing credentials

    request = {
        'labelIds': ['UNREAD'],
        'topicName': topic_name,
        'pushConfig': {
            'url': webhook_url
        }
    }
    print("Subscribed")
    service.users().watch(userId=user_id, body=request).execute()

def mark_as_read(service, msg_id):
    try:
        service.users().messages().modify(
            userId=USER_ID,
            id=msg_id,
            body={
                'removeLabelIds': ['UNREAD']
            }
        ).execute()
    except errors.HttpError as error:
        print(f'An error occurred: {error}')

def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File {file_path} has been deleted successfully")
        except OSError as e:
            print(f"Error: {e.strerror}")
    else:
        print(f"File {file_path} does not exist")

def process_email(service, msg_id):
    print(f"Processing email with id {msg_id}")
    txt = service.users().messages().get(userId=USER_ID, id=msg_id).execute()

    mark_as_read(service, msg_id)

    payload = txt['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body'].get('id') or part['body'].get('attachmentId')
                    if att_id:
                        att = service.users().messages().attachments().get(
                            userId=USER_ID, messageId=msg_id, id=att_id).execute()
                        data = att['data']
                    else:
                        continue

                file_data = base64.urlsafe_b64decode(data)
                file_path = "data/" + part['filename']

                with open(file_path, 'wb') as f:
                    f.write(file_data)

                pdf_text = process_pdf(file_path)

                print(f"Deleting file {file_path}")
                delete_file(file_path)
                subscribe_to_gmail('me', TOPIC_NAME, WEBHOOK_URL)


def get_unread_emails(service):
    results = service.users().messages().list(userId=USER_ID, labelIds=['INBOX', 'UNREAD']).execute()
    return results.get('messages', [])

def main(msg_id=None):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    user_id = 'me'

    if msg_id == None:
        results = service.users().messages().list(userId=user_id, labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])

        for msg in messages:
            process_email(service, msg['id'])

if __name__ == "__main__":
    main()
