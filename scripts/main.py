from __future__ import print_function
import os.path
import re
import html
import unicodedata
import base64
from email.utils import parsedate_to_datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/calendar.events']

def auth_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        print("Opening browser for Google login... (check your browser window)")
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def clean_text(text):
    text = html.unescape(text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Cf')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_body(payload):
    """Recursively extract plain text body from email payload."""
    if payload.get('mimeType') == 'text/plain':
        data = payload.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    for part in payload.get('parts', []):
        result = extract_body(part)
        if result:
            return result
    return ''

def fetch_emails(service):
    try:
        emails = []
        next_page_token = None

        while True:
            results = service.users().messages().list(
                userId='me',
                q='newer_than:1d',  # last 24 hours
                pageToken=next_page_token
            ).execute()

            messages = results.get('messages', [])
            for msg in messages:
                msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
                date = next((h['value'] for h in headers if h['name'] == 'Date'), "")
                body = clean_text(extract_body(msg_data['payload']))
                if not body:
                    body = clean_text(msg_data.get('snippet', ''))
                emails.append({'subject': subject, 'from': sender, 'date': date, 'body': body})

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        return emails

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def main():
    creds = auth_google()
    service = build('gmail', 'v1', credentials=creds)
    emails = fetch_emails(service)
    emails.sort(key=lambda e: parsedate_to_datetime(e['date']) if e['date'] else 0, reverse=True)
    print(f"Total emails: {len(emails)}")
    print("=" * 60)
    for email in emails:
        print(f"From: {email['from']}")
        print(f"Date: {email['date']}")
        print(f"Subject: {email['subject']}")
        print(f"Body:\n{email['body']}")
        print("=" * 60)

if __name__ == '__main__':
    main()