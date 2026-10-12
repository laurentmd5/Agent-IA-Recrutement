import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import google.generativeai as genai
import json

# Setup Deepseek (via OpenAI compatible client)
# Pour DeepSeek, on utilise généralement la base URL de leur API et une clé API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1") if DEEPSEEK_API_KEY else None

# Setup Gemini Fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def call_llm(prompt: str, json_response: bool = True) -> str:
    """
    Appelle DeepSeek en premier, et utilise Gemini 2.0 Flash en fallback en cas d'erreur.
    """
    try:
        if not client:
            raise ValueError("DeepSeek client not configured.")
        
        response = client.chat.completions.create(
            model="deepseek-chat", # ou "deepseek-coder" selon besoin
            messages=[
                {"role": "system", "content": "Tu es un expert RH et un agent de recrutement IA. Réponds uniquement en format JSON." if json_response else "Tu es un expert RH et un agent de recrutement IA."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} if json_response else None,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"DeepSeek failed: {e}. Falling back to Gemini 2.0 Flash.")
        if not GEMINI_API_KEY:
            raise ValueError("Gemini client not configured for fallback.")
        
        # Fallback to Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Gemini ne supporte pas toujours response_format="json_object" de la même manière, on force via le prompt
        fallback_prompt = prompt
        if json_response:
            fallback_prompt += "\n\nCRITICAL: You MUST return ONLY valid JSON."
            
        response = model.generate_content(fallback_prompt)
        text = response.text
        
        # Nettoyage si Gemini a rajouté des balises markdown
        if json_response:
            text = text.replace("```json", "").replace("```", "").strip()
        return text

def extract_cv_data(cv_text: str) -> dict:
    prompt = f"""
    Analyse le CV suivant et extrait les informations en respectant strictement la structure JSON demandée.
    CV:
    {cv_text}
    
    Structure JSON attendue:
    {{
        "full_name": "string",
        "current_position": "string",
        "total_experience_years": int,
        "skills": [{{"name": "string", "years": int, "level": int (1-5)}}],
        "education": [{{"degree": "string", "field": "string", "year": int}}],
        "languages": [{{"name": "string", "level": "string"}}],
        "soft_skills": ["string"]
    }}
    """
    result = call_llm(prompt)
    return json.loads(result)

def extract_job_criteria(job_description: str) -> dict:
    prompt = f"""
    Analyse cette description d'offre d'emploi et extrais les critères en respectant la structure JSON demandée.
    Offre:
    {job_description}
    
    Structure JSON attendue:
    {{
        "job_title": "string",
        "required_skills": [{{"name": "string", "min_years": int, "priority": "obligatoire" ou "souhaité"}}],
        "bonus_skills": [{{"name": "string", "priority": "souhaité"}}],
        "education_level": "string",
        "min_experience": int,
        "languages": [{{"name": "string", "level": "string"}}],
        "soft_skills": ["string"]
    }}
    """
    result = call_llm(prompt)
    return json.loads(result)

def match_profile(cv_json: dict, job_criteria: dict) -> dict:
    prompt = f"""
    Compare le CV JSON suivant avec les critères de l'offre JSON.
    CV: {json.dumps(cv_json, ensure_ascii=False)}
    Offre: {json.dumps(job_criteria, ensure_ascii=False)}
    
    Pour chaque compétence requise de l'offre, vérifie si elle est présente dans le CV (ou une compétence équivalente).
    Génère un JSON avec les correspondances:
    {{
        "matches": [
            {{"critere": "Nom de la compétence de l'offre", "status": "✅" ou "⚠️" ou "❌", "score": float (0 a 100), "cv": "Détail trouvé dans CV", "offre": "Détail exigé", "note": "Explication"}}
        ],
        "experience_match": {{"cv_total": int, "offre_min": int, "status": "✅" ou "❌", "score": float}},
        "education_match": {{"cv": "Niveau CV", "offre": "Niveau requis", "status": "✅" ou "❌", "score": float}},
        "languages_match": {{"cv": "Langue trouvée", "offre": "Langue requise", "status": "✅" ou "❌", "score": float}}
    }}
    """
    result = call_llm(prompt)
    return json.loads(result)
