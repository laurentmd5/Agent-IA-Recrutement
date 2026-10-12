from fastapi import APIRouter, Request, BackgroundTasks
from models.schemas import CandidaturePayload
from workers.tasks import process_candidature_task

router = APIRouter()

@router.post("/candidature", status_code=202)
async def receive_candidature(request: Request, background_tasks: BackgroundTasks):
    # In a real scenario with multipart form data (if file is sent directly), we parse it.
    # However, since the Node.js backend saves the file and passes the path, 
    # we can just receive the JSON or form data.
    
    # We use BackgroundTasks for a simple queue without Redis initially,
    # or we can push to RQ if Redis is available.
    # Since Redis is installed, let's use RQ.
    
    try:
        form_data = await request.form()
        payload = {
            "candidature_id": form_data.get("candidatureId"),
            "job_id": form_data.get("jobTitle"), # We use jobTitle for now or adapt Node.js to send jobId
            "first_name": form_data.get("firstName"),
            "last_name": form_data.get("lastName"),
            "email": form_data.get("email"),
            "phone": form_data.get("phone", ""),
            "job_title": form_data.get("jobTitle"),
            "message": form_data.get("message", ""),
            "cv_file_path": "", # Will be set below
            "cv_filename": "",
            "submitted_at": form_data.get("createdAt")
        }
        
        cv_file = form_data.get("cv")
        if cv_file:
            # We save the file locally in the agent, or we read the path if Node sent a path
            # Actually Node.js is sending the file stream in the webhook.
            import os
            os.makedirs("uploads", exist_ok=True)
            file_path = f"uploads/{cv_file.filename}"
            with open(file_path, "wb") as f:
                f.write(await cv_file.read())
            payload["cv_file_path"] = file_path
            payload["cv_filename"] = cv_file.filename

        # Utilisation de BackgroundTasks de FastAPI (plus stable sous Windows que RQ)
        background_tasks.add_task(process_candidature_task, payload)
        
        return {"status": "Accepted", "job_id": "fastapi-bg-task"}

    except Exception as e:
        import traceback
        with open("webhook_error.log", "a") as f:
            f.write(traceback.format_exc() + "\n")
        print(f"Webhook Error: {e}")
        return {"error": str(e)}

from pydantic import BaseModel
class ForceQuestionnairePayload(BaseModel):
    candidature_id: str
    email: str
    first_name: str
    job_title: str

@router.post("/force-questionnaire", status_code=202)
async def force_questionnaire(payload: ForceQuestionnairePayload, background_tasks: BackgroundTasks):
    try:
        from services.email_service import send_top_candidate_email
        print(f"Forçage manuel du questionnaire pour {payload.candidature_id} ({payload.email})")
        background_tasks.add_task(
            send_top_candidate_email,
            candidate_email=payload.email,
            candidate_name=payload.first_name,
            job_title=payload.job_title,
            candidature_id=payload.candidature_id
        )
        return {"status": "Accepted", "message": "Email en cours d'envoi"}
    except Exception as e:
        return {"error": str(e)}
