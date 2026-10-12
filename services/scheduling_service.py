from datetime import datetime, timedelta
import random

def get_next_interview_slot() -> tuple[str, str]:
    """
    Calcule le créneau d'entretien pour le "lendemain" (du lundi au vendredi).
    L'heure est générée aléatoirement entre 09:30 et 15:00.
    Retourne un tuple (date_str, time_str) formaté.
    """
    now = datetime.now()
    
    # +1 jour par défaut
    next_day = now + timedelta(days=1)
    
    # Vérifier le jour de la semaine (0 = Lundi, 5 = Samedi, 6 = Dimanche)
    if next_day.weekday() == 5: # Samedi
        next_day = next_day + timedelta(days=2) # Lundi
    elif next_day.weekday() == 6: # Dimanche
        next_day = next_day + timedelta(days=1) # Lundi

    # Heure aléatoire entre 09:30 et 15:00
    # On peut générer par créneaux de 30 minutes
    # 09:30 = 9.5
    # 15:00 = 15.0
    possible_hours = [
        "09:30", "10:00", "10:30", "11:00", 
        "11:30", "13:30", "14:00", "14:30", "15:00"
    ]
    
    selected_time = random.choice(possible_hours)
    
    # Format de la date: 'Jeudi 15 Octobre 2026' ou 'YYYY-MM-DD'
    date_str = next_day.strftime("%d/%m/%Y")
    
    return date_str, selected_time
