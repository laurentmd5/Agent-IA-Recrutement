from fastapi import APIRouter
from services.gmail_collector import collector

router = APIRouter()

@router.post("/gmail")
def trigger_gmail_sync():
    """
    Déclenche la synchronisation des candidatures depuis Gmail.
    Applique le filtrage strict à 3 niveaux :
    1. Dossier cloisonné ('Candidatures')
    2. Pièce jointe CV obligatoire (.pdf, .docx, .doc)
    3. Mots-clés de recrutement (Objet/Corps) + Blacklist anti-spam
    """
    result = collector.sync_candidatures()
    return result

@router.get("/gmail/status")
def get_sync_status():
    return {
        "status": "ready",
        "account": collector.user,
        "target_folder": collector.target_folder,
        "node_api_url": collector.node_api_url
    }
