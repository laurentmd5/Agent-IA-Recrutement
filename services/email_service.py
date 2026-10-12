import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_top_candidate_email(candidate_email: str, candidate_name: str, job_title: str, candidature_id: str):
    """
    Envoie un email personnalisé au top candidat pour lui demander de remplir le questionnaire.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass or "votre_email" in smtp_user:
        print("Avertissement: Configuration SMTP manquante ou non configurée, email ignoré.")
        return

    msg = MIMEMultipart()
    msg['From'] = f"NetSystème Recrutement <{smtp_user}>"
    msg['To'] = candidate_email
    msg['Subject'] = f"Félicitations - Étape suivante pour le poste de {job_title}"

    # Note: Frontend URL should ideally come from env, hardcoded for now
    questionnaire_link = f"http://localhost:3000/candidature/questionnaire/{candidature_id}"

    body = f"""Bonjour {candidate_name},

Nous avons bien reçu votre candidature et nous vous remercions de l’intérêt que vous portez à notre entreprise.

Afin de mieux évaluer votre profil, nous vous invitons à répondre aux questions suivantes :

1. Avez-vous bien pris connaissance de notre offre de stage ? Comme indiqué dans l’annonce, il s’agit d’un stage pouvant déboucher sur un contrat en fonction de vos performances.
2. Quelle est votre disponibilité pour commencer le stage ?
3. Êtes-vous informé(e) que ce stage n’est pas rémunéré ? En revanche, si vos performances sont satisfaisantes et que vous faites preuve d’efficacité, nous pourrons réévaluer cette situation et envisager une prise en charge de vos frais de transport, ainsi qu’une éventuelle évolution vers un contrat.
4. Quelles sont vos principales compétences techniques et professionnelles ?
5. Avez-vous déjà effectué des travaux de terrain ? Si oui, merci de préciser dans quel domaine et de décrire brièvement votre expérience.

Veuillez cliquer sur le lien ci-dessous pour soumettre vos réponses à ce questionnaire :
{questionnaire_link}

Nous vous remercions pour vos réponses et restons à votre disposition pour toute information complémentaire.

Cordialement,
L'équipe Recrutement de NetSystème
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Email de questionnaire envoyé avec succès à {candidate_email}.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email à {candidate_email}: {e}")

def send_interview_invitation_email(candidate_email: str, candidate_name: str, job_title: str, date_str: str, time_str: str):
    """
    Envoie l'invitation finale à l'entretien si l'IA valide le questionnaire.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass or "votre_email" in smtp_user:
        return

    msg = MIMEMultipart()
    msg['From'] = f"NetSystème Recrutement <{smtp_user}>"
    msg['To'] = candidate_email
    msg['Subject'] = f"Convocation à un entretien - {job_title}"

    body = f"""Bonjour {candidate_name},

Nous avons bien reçu vos réponses à notre questionnaire et nous vous en remercions. Celles-ci correspondent parfaitement à nos attentes.

Nous avons le plaisir de vous inviter à un entretien de recrutement dans nos locaux pour discuter plus en détail de votre profil.

Date : {date_str}
Heure : {time_str}

Merci de nous confirmer votre présence en répondant à ce mail.

Cordialement,
L'équipe Recrutement de NetSystème
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Email de convocation envoyé avec succès à {candidate_email} pour le {date_str} à {time_str}.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la convocation à {candidate_email}: {e}")

