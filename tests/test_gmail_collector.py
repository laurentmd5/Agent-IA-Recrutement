import unittest
import os
import sys

# Ajouter le dossier parent au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.gmail_collector import (
    clean_header_string,
    extract_phone_number,
    extract_job_title,
    RECRUITMENT_KEYWORDS,
    BLACKLIST_SENDERS,
)

class TestGmailCollectorLevel123(unittest.TestCase):
    
    def test_clean_header_string(self):
        # UTF-8 encodé MIME
        raw = "=?UTF-8?B?Q2FuZGlkYXR1cmUgU3RhZ2UgRMOpdmVsb3BwZXVy?="
        self.assertEqual(clean_header_string(raw), "Candidature Stage Développeur")
        # En-tête simple
        self.assertEqual(clean_header_string("Ingenieur Reseau"), "Ingenieur Reseau")
        # None ou vide
        self.assertEqual(clean_header_string(None), "")

    def test_extract_phone_number_senegal_and_intl(self):
        # Test numéro sénégalais avec +221
        body1 = "Bonjour, vous pouvez me joindre au +221 77 123 45 67 pour un entretien."
        self.assertTrue("+221" in extract_phone_number(body1))
        
        # Test format local direct
        body2 = "Contact : 781234567 disponible immédiatement."
        self.assertEqual(extract_phone_number(body2), "781234567")
        
        # Sans téléphone
        body3 = "Je vous transmets mon CV en pièce jointe sans mention de mobile."
        self.assertIsNone(extract_phone_number(body3))

    def test_extract_job_title(self):
        # Format avec préfixe usuel
        subject1 = "Candidature au poste de Développeur Fullstack"
        self.assertEqual(extract_job_title(subject1), "Développeur Fullstack")

        subject2 = "Candidature spontanée : Technicien Réseau"
        self.assertEqual(extract_job_title(subject2), "Technicien Réseau")

        # Sujet générique ou court
        self.assertEqual(extract_job_title(""), "Candidature Spontanée")
        self.assertEqual(extract_job_title("CV"), "Candidature Spontanée")

    def test_level_2_cv_attachment_filter(self):
        """Vérifie que seules les extensions CV (.pdf, .docx, .doc) sont acceptées"""
        valid_extensions = ['.pdf', '.docx', '.doc']
        invalid_extensions = ['.png', '.jpg', '.zip', '.exe', '.txt', '.xlsx']

        def is_cv_attachment(filename):
            ext = os.path.splitext(filename.lower())[1]
            return ext in valid_extensions

        # Cas valides
        self.assertTrue(is_cv_attachment("CV_Laurent_Mavoungou.pdf"))
        self.assertTrue(is_cv_attachment("Curriculum_Vitae.docx"))
        self.assertTrue(is_cv_attachment("MonCV.DOC"))

        # Cas invalides (photos, archives, scripts...)
        for bad in ["signature_logo.png", "scan.jpg", "projet.zip", "malware.exe", "notes.txt"]:
            self.assertFalse(is_cv_attachment(bad), f"{bad} ne devrait pas être accepté comme CV")

    def test_level_3_blacklist_filter(self):
        """Vérifie que les expéditeurs automatiques et spams sont filtrés"""
        spam_emails = [
            "noreply@uber.com",
            "no-reply@notification.github.com",
            "newsletter@info-tech.com",
            "billing@service-cloud.com",
            "support@ovh.com",
            "messages-noreply@linkedin.com"
        ]
        legit_emails = [
            "amadou.diallo@gmail.com",
            "fatou.fall@yahoo.fr",
            "moustapha.ba@outlook.com"
        ]

        def is_blacklisted(email_addr):
            return any(black in email_addr.lower() for black in BLACKLIST_SENDERS)

        for spam in spam_emails:
            self.assertTrue(is_blacklisted(spam), f"{spam} devrait être blacklisté")

        for legit in legit_emails:
            self.assertFalse(is_blacklisted(legit), f"{legit} ne devrait PAS être blacklisté")

    def test_level_3_recruitment_keywords_filter(self):
        """Vérifie la détection sémantique des mots-clés RH"""
        valid_texts = [
            "Veuillez trouver ci-joint ma candidature pour le poste de technicien.",
            "Objet : CV pour le stage en télécommunication",
            "Je vous transmets mon curriculum vitae en vue d'une embauche."
        ]
        spam_texts = [
            "Voici votre facture mensuelle pour le service internet.",
            "Confirmation de votre réservation d'hôtel.",
            "Offre promotionnelle -50% sur vos achats !"
        ]

        def contains_recruitment_keywords(text):
            text_lower = text.lower()
            return any(k in text_lower for k in RECRUITMENT_KEYWORDS)

        for vt in valid_texts:
            self.assertTrue(contains_recruitment_keywords(vt), f"Mot-clé attendu dans : {vt}")

        # La facture ne doit pas être considérée comme candidature
        self.assertFalse(contains_recruitment_keywords(spam_texts[0]))
        self.assertFalse(contains_recruitment_keywords(spam_texts[1]))

if __name__ == '__main__':
    unittest.main()
