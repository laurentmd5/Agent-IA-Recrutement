import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api.webhook import router as webhook_router
from api.webhook_questionnaire import router as questionnaire_router
from api.sync_gmail import router as sync_router
from services.gmail_collector import collector

app = FastAPI(
    title="Agent IA Recruteur",
    description="Agent autonome de traitement et d'ingestion des candidatures pour NetSystème",
    version="1.1.0"
)

app.include_router(webhook_router, prefix="/api/v1/webhook", tags=["Webhook"])
app.include_router(questionnaire_router, prefix="/api/v1/webhook", tags=["Questionnaire"])
app.include_router(sync_router, prefix="/api/v1/sync", tags=["Synchronisation"])

async def periodic_gmail_sync():
    """Tâche de fond s'exécutant toutes les 10 minutes (600 secondes)."""
    # Attente initiale de 10 secondes au démarrage du service
    await asyncio.sleep(10)
    while True:
        try:
            print("[Scheduler] Lancement de la synchronisation périodique Gmail (3 niveaux)...")
            collector.sync_candidatures()
        except Exception as e:
            print(f"[Scheduler] Erreur pendant la synchronisation : {e}")
        await asyncio.sleep(600)

@app.on_event("startup")
async def startup_event():
    # Démarre la boucle de synchronisation en tâche de fond
    asyncio.create_task(periodic_gmail_sync())

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Agent IA Recruteur & Collecteur Gmail"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
