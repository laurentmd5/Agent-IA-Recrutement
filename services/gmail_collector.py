import os
import sys
import re
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def log(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(str(msg).encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            pass

RECRUITMENT_KEYWORDS = [
    'candidature', 'cv', 'recrutement', 'stage', 'poste', 'emploi', 
    'motivation', 'postuler', 'curriculum vitae', 'curriculum',
    'developpeur', 'ingenieur', 'technicien', 'commercial', 'comptable',
    'alternance', 'offre', 'embauche'
]

BLACKLIST_SENDERS = [
    'no-reply', 'noreply', 'mailer-daemon', 'notification', 'notifications',
    'donotreply', 'newsletter', 'accounts.google.com', 'linkedin.com', 'github.com',
    'alert', 'billing', 'invoice', 'facture', 'support@'
]

def clean_header_string(header_val):
    if not header_val:
        return ""
    decoded_fragments = decode_header(header_val)
    parts = []
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            try:
                parts.append(fragment.decode(encoding or 'utf-8', errors='ignore'))
            except Exception:
                parts.append(fragment.decode('latin-1', errors='ignore'))
        else:
            parts.append(str(fragment))
    return "".join(parts).strip()

def extract_phone_number(text):
    if not text:
        return None
    # Détection numéros internationaux ou sénégalais (+221, 77, 78, 76, 70...)
    pattern = r'(?:\+?221\s?)?(?:7[05678]\d{7}|33\d{7}|\b\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b)'
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None

def extract_job_title(subject):
    if not subject:
        return "Candidature Spontanée"
    # Nettoie les préfixes comme "Candidature au poste de..."
    cleaned = re.sub(r'^(candidature\s*(spontanée|pour|au poste de|pour le poste de)?\s*:?\s*)', '', subject, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned if len(cleaned) > 2 else "Candidature Spontanée"

class GmailCollector:
    def __init__(self):
        self.imap_host = os.getenv("IMAP_HOST", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        self.target_folder = os.getenv("GMAIL_FOLDER", "Candidatures")
        self.node_api_url = os.getenv("NODE_API_URL", "http://localhost:5001/api").rstrip('/')
        self.service_key = os.getenv("INTERNAL_SERVICE_KEY", "netsys-internal-key-2026")

    def sync_candidatures(self):
        """
        Scanne la boîte Gmail avec les 3 niveaux de filtrage stricts :
        1. Dossier spécifique ('Candidatures')
        2. Pièce jointe obligatoire (.pdf, .docx, .doc)
        3. Mots-clés de recrutement obligatoires (Objet/Corps) + Blacklist
        """
        if not self.user or not self.password:
            print("[GmailCollector] Identifiants Gmail manquants dans le .env.")
            return {"status": "error", "message": "Identifiants Gmail manquants (SMTP_USER / SMTP_PASS)."}

        print(f"[GmailCollector] Connexion à {self.imap_host} pour {self.user}...")
        report = {
            "status": "success",
            "folder_used": self.target_folder,
            "emails_found": 0,
            "processed": 0,
            "skipped_no_cv": 0,
            "skipped_keywords": 0,
            "skipped_blacklist": 0,
            "details": []
        }

        mail = None
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.user, self.password)

            # NIVEAU 1 : Sélection du dossier cloisonné
            selected_folder = self.target_folder
            status, _ = mail.select(f'"{self.target_folder}"')
            if status != 'OK':
                print(f"[GmailCollector] Dossier '{self.target_folder}' introuvable, repli sur 'INBOX'...")
                status, _ = mail.select("INBOX")
                selected_folder = "INBOX"

            report["folder_used"] = selected_folder

            # Recherche des e-mails non lus
            status, search_data = mail.search(None, "UNSEEN")
            if status != 'OK' or not search_data or not search_data[0]:
                print("[GmailCollector] Aucun nouvel e-mail non lu trouvé.")
                return report

            email_ids = search_data[0].split()
            report["emails_found"] = len(email_ids)
            # Analyser les plus récents en premier (l'e-mail fraîchement envoyé est en tête)
            recent_email_ids = list(reversed(email_ids))[:100]
            log(f"[GmailCollector] {len(email_ids)} e-mail(s) non lu(s) au total. Analyse prioritaire des {len(recent_email_ids)} plus récents...")

            for e_id in recent_email_ids:
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                if res != 'OK':
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Extraction en-têtes
                subject = clean_header_string(msg.get("Subject", ""))
                from_raw = clean_header_string(msg.get("From", ""))
                sender_name, sender_email = parseaddr(from_raw)
                message_id = msg.get("Message-ID", f"msg-{e_id.decode()}")

                # NIVEAU 3.A : Vérification Blacklist
                if any(black in sender_email.lower() for black in BLACKLIST_SENDERS):
                    log(f"[GmailCollector] E-mail ignore (Blacklist) : {sender_email}")
                    report["skipped_blacklist"] += 1
                    continue

                # Extraction corps de message
                body_text = ""
                attachments = []

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition", ""))

                        # Texte
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                body_text += part.get_payload(decode=True).decode('utf-8', errors='ignore') + "\n"
                            except Exception:
                                pass
                        elif content_type == "text/html" and "attachment" not in content_disposition and not body_text:
                            try:
                                raw_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                # Nettoyage sommaire HTML
                                body_text += re.sub(r'<[^>]+>', ' ', raw_html) + "\n"
                            except Exception:
                                pass

                        # Pièces jointes
                        filename = part.get_filename()
                        if filename:
                            clean_filename = clean_header_string(filename)
                            file_ext = os.path.splitext(clean_filename.lower())[1]
                            if file_ext in ['.pdf', '.docx', '.doc']:
                                resolved_mime = content_type
                                if file_ext == '.pdf':
                                    resolved_mime = 'application/pdf'
                                elif file_ext == '.docx':
                                    resolved_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                elif file_ext == '.doc':
                                    resolved_mime = 'application/msword'

                                attachments.append({
                                    "filename": clean_filename,
                                    "payload": part.get_payload(decode=True),
                                    "mimetype": resolved_mime
                                })
                else:
                    try:
                        body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        body_text = str(msg.get_payload())

                # NIVEAU 2 : Pièce jointe obligatoire (CV)
                if not attachments:
                    log(f"[GmailCollector] E-mail ignore : pas de fichier CV joint ({subject})")
                    report["skipped_no_cv"] += 1
                    continue

                # NIVEAU 3.B : Mots-clés de recrutement obligatoires (Objet ou Corps)
                text_to_check = f"{subject} {body_text}".lower()
                has_keyword = any(k in text_to_check for k in RECRUITMENT_KEYWORDS)
                
                # Si l'e-mail est dans le dossier dédié 'Candidatures', on est plus tolérant
                if selected_folder != "Candidatures" and not has_keyword:
                    log(f"[GmailCollector] E-mail ignore (aucun mot-cle de candidature) : '{subject}'")
                    report["skipped_keywords"] += 1
                    continue

                # C'est une vraie candidature valide !
                best_cv = attachments[0]
                detected_phone = extract_phone_number(body_text)
                detected_job = extract_job_title(subject)
                candidate_full_name = sender_name or sender_email.split('@')[0]

                log(f"[GmailCollector] [CANDIDATURE DETECTEE] : {candidate_full_name} ({sender_email}) pour '{detected_job}'")

                # Envoi au backend Node.js
                payload = {
                    "fullName": candidate_full_name,
                    "email": sender_email,
                    "phone": detected_phone or "",
                    "jobTitle": detected_job,
                    "message": body_text[:2000].strip(),
                    "source": "GMAIL_DG",
                    "status": "NOUVEAU",
                    "gmailMessageId": message_id
                }

                files = {
                    'cv': (best_cv['filename'], best_cv['payload'], best_cv['mimetype'])
                }

                headers = {
                    'X-Service-Key': self.service_key
                }

                try:
                    res = requests.post(
                        f"{self.node_api_url}/recrutement/manual",
                        data=payload,
                        files=files,
                        headers=headers,
                        timeout=15
                    )
                    
                    if res.status_code in [200, 201]:
                        report["processed"] += 1
                        report["details"].append({
                            "candidate": candidate_full_name,
                            "email": sender_email,
                            "job": detected_job,
                            "status": "imported"
                        })
                        log(f"[GmailCollector] Ingestion reussie en BDD pour {sender_email}")
                        # Marquer l'e-mail comme lu
                        mail.store(e_id, '+FLAGS', '\\Seen')
                    elif res.status_code == 400 and 'duplicate' in res.text.lower():
                        report["processed"] += 1
                        log(f"[GmailCollector] E-mail deja en base : {sender_email}")
                        mail.store(e_id, '+FLAGS', '\\Seen')
                    else:
                        log(f"[GmailCollector] Erreur API Node.js ({res.status_code}) : {res.text}")
                except Exception as api_err:
                    log(f"[GmailCollector] Erreur appel API Node : {api_err}")

            return report

        except Exception as e:
            log(f"[GmailCollector] Erreur generale : {e}")
            return {"status": "error", "error": str(e)}
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass

collector = GmailCollector()
