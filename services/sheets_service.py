import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'credentials.json')
    if not os.path.exists(creds_path):
        print(f"Warning: {creds_path} not found. Sheets integration disabled.")
        return None
        
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def append_candidature_row(payload: dict, cv_json: dict, final_result: any):
    """
    Ajoute une ligne dans le Google Sheet (Onglet 'Candidatures').
    """
    service = get_sheets_service()
    if not service:
        return
        
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    if not sheet_id:
        return
        
    # Format the row according to the 19 columns found in the Google Sheet
    row = [
        payload.get("candidature_id", ""),  # 1: ID
        payload.get("submitted_at", ""),    # 2: Date
        f"{payload.get('first_name', '')} {payload.get('last_name', '')}",  # 3: Nom complet
        payload.get("email", ""),           # 4: Email
        payload.get("phone", ""),           # 5: Téléphone
        payload.get("job_title", ""),       # 6: Poste visé
        final_result.final_score,           # 7: Score/10
        cv_json.get("total_experience_years", 0),  # 8: Années XP
        ", ".join([s.get("name", "") for s in cv_json.get("skills", [])]),  # 9: Compétences
        "",                                 # 10: Forces
        "",                                 # 11: Faiblesses
        final_result.justification,         # 12: Synthèse
        final_result.decision,              # 13: Recommandation
        cv_json.get("current_position", ""),# 14: Poste actuel
        ", ".join([e.get("degree", "") for e in cv_json.get("education", [])]), # 15: Diplômes
        ", ".join([l.get("name", "") for l in cv_json.get("languages", [])]),   # 16: Langues
        payload.get("cv_file_path", ""),    # 17: Lien CV
        "NOUVEAU",                          # 18: Recommandation finale
        ""                                  # 19: Date réponse
    ]
    
    try:
        body = {'values': [row]}
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Candidatures!A:S",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        print(f"{result.get('updates').get('updatedCells')} cells appended to Sheets.")
    except Exception as e:
        print(f"Failed to append to Google Sheets: {e}")
