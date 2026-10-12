import sys
import traceback
from workers.tasks import process_candidature_task
from dotenv import load_dotenv

load_dotenv()

payload = {
    "candidature_id": "SIM_E2E_001",
    "job_title": "Développeur Full Stack Senior H/F",
    "first_name": "Didier",
    "last_name": "Test",
    "email": "didieriwandza02@gmail.com",
    "phone": "0102030405",
    "cv_file_path": "uploads/test.pdf", # We'll create a fake one
}

import os
os.makedirs("uploads", exist_ok=True)
with open("uploads/test.pdf", "wb") as f:
    f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Test CV content) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000227 00000 n \n0000000320 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n408\n%%EOF\n")

print("Starting simulation...", flush=True)
import unittest.mock as mock

fake_cv_text = """
Je suis Didier Test, Développeur Full Stack Senior H/F avec 10 ans d'expérience. 
Je maîtrise parfaitement React, Node.js, Python, AWS, Docker, et Kubernetes.
J'ai un diplôme d'ingénieur (Bac+5).
Mes expériences passées prouvent ma capacité à gérer des projets de bout en bout.
"""

from models.schemas import MatchingResult

try:
    with mock.patch("workers.tasks.parse_cv") as mock_parse, \
         mock.patch("workers.tasks.calculate_score") as mock_score:
        
        mock_parse.return_value = fake_cv_text
        mock_score.return_value = MatchingResult(
            final_score=95,
            decision="AUTO-ACCEPT",
            justification="Profil exceptionnel pour les tests."
        )
        process_candidature_task(payload)
    print("Simulation finished successfully.", flush=True)
except Exception as e:
    print(f"Simulation failed: {e}", flush=True)
    traceback.print_exc()
