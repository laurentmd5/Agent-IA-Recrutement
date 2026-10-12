import os
from services.document_parser import parse_cv
from services.llm_service import extract_cv_data, extract_job_criteria, match_profile
from services.scoring_engine import calculate_score
from services.sheets_service import append_candidature_row
from services.email_service import send_top_candidate_email

def process_candidature_task(payload: dict):
    """
    Tâche exécutée en arrière-plan par le worker RQ (Redis Queue).
    """
    try:
        with open("task_debug.log", "a", encoding="utf-8") as f:
            f.write(f"--- START Processing candidature {payload['candidature_id']}...\n")
        print(f"Processing candidature {payload['candidature_id']}...", flush=True)
        
        # 1. Extraction du texte du CV
        cv_text = parse_cv(payload['cv_file_path'])
        
        # 2. LLM : Structurer le CV
        cv_json = extract_cv_data(cv_text)
        
        # 3. Récupérer l'offre d'emploi depuis l'API Node.js
        # (Pour simplifier ici, on utilise job_title, mais idéalement on fetch de l'API Node)
        import requests
        node_api = os.getenv("NODE_API_URL", "http://localhost:5000/api")
        # req = requests.get(f"{node_api}/jobs?title={payload['job_title']}")
        # Pour l'exemple, on simule la description récupérée
        job_description = "Description de l'offre pour " + payload['job_title']
        
        # 4. LLM : Extraire les critères de l'offre
        job_criteria = extract_job_criteria(job_description)
        
        # 5. LLM : Matching
        match_result = match_profile(cv_json, job_criteria)
        
        # 6. Moteur de scoring & décision
        final_result = calculate_score(match_result)
        
        # 7. Sauvegarde dans Google Sheets
        append_candidature_row(payload, cv_json, final_result)
        
        # 8. Action (PATCH API / Envoi d'email) - Géré par l'engine ou un autre service
        if final_result.decision == "AUTO-ACCEPT":
            print("Candidat de type AUTO-ACCEPT, envoi de l'email...")
            send_top_candidate_email(
                candidate_email=payload['email'],
                candidate_name=payload['first_name'],
                job_title=payload['job_title'],
                candidature_id=payload['candidature_id']
            )

        with open("task_debug.log", "a", encoding="utf-8") as f:
            f.write(f"--- SUCCESS Candidature {payload['candidature_id']} processed. Decision: {final_result.decision}\n")
        print(f"Candidature {payload['candidature_id']} processed successfully. Decision: {final_result.decision}", flush=True)
        return True
    except Exception as e:
        with open("task_debug.log", "a", encoding="utf-8") as f:
            import traceback
            f.write(f"--- ERROR Processing candidature {payload['candidature_id']}: {e}\n")
            f.write(traceback.format_exc() + "\n")
        print(f"Error processing candidature {payload['candidature_id']}: {e}", flush=True)
        return False
