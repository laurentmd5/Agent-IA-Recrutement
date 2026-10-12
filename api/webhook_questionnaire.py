from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.schemas import QuestionnairePayload
from services.questionnaire_evaluator import evaluate_questionnaire
from services.scheduling_service import get_next_interview_slot
from services.email_service import send_interview_invitation_email
import json

router = APIRouter()

def process_questionnaire_task(payload: QuestionnairePayload):
    """
    Tâche de fond pour évaluer le questionnaire.
    """
    print(f"Évaluation du questionnaire pour la candidature {payload.candidature_id}...")
    
    expected_criteria = """
    - Le candidat doit confirmer avoir pris connaissance de l'offre et comprendre la possibilité d'évolution vers un contrat.
    - Il doit donner sa disponibilité de manière claire.
    - Il doit accepter explicitement que le stage ne soit pas rémunéré dans un premier temps.
    - Il doit lister des compétences techniques pertinentes.
    - S'il a une expérience terrain, il doit la décrire. L'absence d'expérience terrain n'est pas éliminatoire, mais le refus de répondre ou une réponse arrogante l'est.
    - L'attitude globale doit être motivée et professionnelle.
    """
    
    # 1. Évaluation par l'IA
    result = evaluate_questionnaire(payload.answers, expected_criteria)
    
    print(f"Résultat pour {payload.candidature_id} : {'SUCCÈS' if result.passed else 'ÉCHEC'} - {result.justification}")
    
    # 2. Si succès, planifier l'entretien
    if result.passed:
        date_str, time_str = get_next_interview_slot()
        print(f"Planification de l'entretien le {date_str} à {time_str}")
        
        # 3. Envoyer l'invitation
        send_interview_invitation_email(
            candidate_email=payload.candidate_email,
            candidate_name=payload.candidate_name,
            job_title=payload.job_title,
            date_str=date_str,
            time_str=time_str
        )
    else:
        # Optionnel: Envoyer un email de refus automatique
        print(f"Candidat rejeté après questionnaire. Justification: {result.justification}")
        
    return True

@router.post("/questionnaire", status_code=202)
async def submit_questionnaire(payload: QuestionnairePayload, background_tasks: BackgroundTasks):
    """
    Reçoit les réponses au questionnaire et lance l'évaluation en arrière-plan.
    """
    try:
        background_tasks.add_task(process_questionnaire_task, payload)
        return {"status": "accepted", "message": "Réponses reçues et en cours d'analyse par l'IA"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
