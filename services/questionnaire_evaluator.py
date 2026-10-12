import json
from services.llm_service import call_llm
from models.schemas import EvaluationResult

def evaluate_questionnaire(answers: dict, expected_criteria: str) -> EvaluationResult:
    """
    Évalue les réponses au questionnaire d'un candidat à l'aide du LLM.
    Retourne un EvaluationResult (passed: bool, justification: str).
    """
    
    prompt = f"""
Tu es un recruteur expert pour NetSystème.
Tu dois évaluer les réponses d'un candidat à un questionnaire de pré-sélection.

CRITÈRES ET ATTENTES DE L'ENTREPRISE :
{expected_criteria}

RÉPONSES DU CANDIDAT :
{json.dumps(answers, ensure_ascii=False, indent=2)}

INSTRUCTIONS :
1. Analyse chaque réponse du candidat.
2. Vérifie si elles correspondent globalement aux attentes et critères de l'entreprise.
3. Détermine si le candidat "passe" cette étape (true) ou "échoue" (false). Pour passer, les réponses doivent démontrer de la motivation, de la cohérence, et répondre positivement aux critères éliminatoires s'il y en a.
4. Rédige une justification courte (1 à 2 phrases).

Tu dois répondre UNIQUEMENT par un objet JSON valide avec cette structure stricte :
{{
    "passed": true ou false,
    "justification": "Explication de la décision"
}}
"""
    
    try:
        response_text = call_llm(prompt)
        
        # Clean potential markdown wrapping
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        data = json.loads(response_text.strip())
        return EvaluationResult(
            passed=bool(data.get("passed", False)),
            justification=str(data.get("justification", "Pas de justification"))
        )
    except Exception as e:
        print(f"Erreur lors de l'évaluation du questionnaire: {e}")
        # En cas d'erreur de parsing ou d'API, on est prudent et on rejette (ou on met en attente manuelle)
        return EvaluationResult(
            passed=False,
            justification=f"Erreur d'analyse automatique: {str(e)}"
        )
