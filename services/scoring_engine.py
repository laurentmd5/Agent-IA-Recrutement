from models.schemas import MatchingResult

def calculate_score(match_data: dict) -> MatchingResult:
    """
    Calcule le score final basé sur les pondérations:
    - Tech: 50%
    - XP: 25%
    - Education: 15%
    - Langues & Soft: 10%
    """
    
    # 1. Tech Score
    matches = match_data.get("matches", [])
    if not matches:
        tech_score = 0
    else:
        total_tech = sum(m.get("score", 0) for m in matches)
        tech_score = (total_tech / (len(matches) * 100)) * 10 # Sur 10
        
    tech_weighted = tech_score * 0.50
    
    # 2. Experience Score
    exp = match_data.get("experience_match", {})
    exp_score = (exp.get("score", 0) / 100) * 10
    exp_weighted = exp_score * 0.25
    
    # 3. Education Score
    edu = match_data.get("education_match", {})
    edu_score = (edu.get("score", 0) / 100) * 10
    edu_weighted = edu_score * 0.15
    
    # 4. Languages Score
    lang = match_data.get("languages_match", {})
    lang_score = (lang.get("score", 0) / 100) * 10
    lang_weighted = lang_score * 0.10
    
    final_score = tech_weighted + exp_weighted + edu_weighted + lang_weighted
    
    # Arbre de décision
    if final_score >= 8.0:
        decision = "AUTO-ACCEPT"
        justification = "Profil excellent, correspond parfaitement aux attentes."
    elif 6.0 <= final_score < 8.0:
        decision = "HUMAN REVIEW"
        justification = "Profil intéressant mais nécessite une vérification humaine."
    elif 4.0 <= final_score < 6.0:
        decision = "WAITING LIST"
        justification = "Profil moyen, gardé en réserve."
    else:
        decision = "AUTO-REJECT"
        justification = "Profil ne correspondant pas aux critères minimaux."
        
    result = MatchingResult(
        matches=matches, # Normalement on mappe ça dans les objets MatchItem
        experience_match=exp,
        education_match=edu,
        languages_match=lang,
        final_score=round(final_score, 2),
        decision=decision,
        justification=justification
    )
    
    return result
