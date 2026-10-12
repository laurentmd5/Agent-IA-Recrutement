import requests
import json

def test_questionnaire(passed=True):
    url = "http://127.0.0.1:8000/api/v1/webhook/questionnaire"
    
    if passed:
        answers = {
            "q1": "Je suis extrêmement motivé pour rejoindre NetSystème car vos valeurs me correspondent parfaitement.",
            "q2": "Je suis disponible immédiatement.",
            "q3": "J'ai récemment déployé une infrastructure cloud complète sur AWS en utilisant Terraform."
        }
    else:
        answers = {
            "q1": "Parce que j'ai besoin d'argent.",
            "q2": "Je ne sais pas.",
            "q3": "Rien de spécial."
        }

    payload = {
        "candidature_id": "SIM_E2E_001",
        "candidate_email": "didieriwandza02@gmail.com", # Changez pour tester le vrai envoi
        "candidate_name": "Didier Test",
        "job_title": "Développeur Full Stack Senior H/F",
        "answers": answers
    }

    print(f"Envoi du questionnaire de test (attendu: {'SUCCÈS' if passed else 'ÉCHEC'})...")
    
    try:
        res = requests.post(url, json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Erreur de connexion : {e}")

if __name__ == "__main__":
    import sys
    should_pass = True
    if len(sys.argv) > 1 and sys.argv[1] == "fail":
        should_pass = False
        
    test_questionnaire(should_pass)
