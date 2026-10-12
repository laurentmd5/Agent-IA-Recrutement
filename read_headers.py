import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_headers():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    if not os.path.exists(creds_path):
        print("Credentials not found")
        return
        
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Candidatures!A1:Z1"
    ).execute()
    
    headers = result.get('values', [[]])[0]
    for i, header in enumerate(headers):
        print(f"Col {i+1}: {header}")

if __name__ == '__main__':
    get_headers()
