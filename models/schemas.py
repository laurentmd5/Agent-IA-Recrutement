from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class CandidaturePayload(BaseModel):
    candidature_id: str
    job_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: str
    message: Optional[str] = None
    cv_file_path: str
    cv_filename: str
    submitted_at: str

class Skill(BaseModel):
    name: str
    years: Optional[int] = None
    level: Optional[int] = None

class Education(BaseModel):
    degree: str
    field: str
    year: Optional[int] = None

class Language(BaseModel):
    name: str
    level: str

class CVData(BaseModel):
    full_name: str
    current_position: Optional[str] = None
    total_experience_years: Optional[int] = None
    skills: List[Skill] = []
    education: List[Education] = []
    languages: List[Language] = []
    soft_skills: List[str] = []

class RequiredSkill(BaseModel):
    name: str
    min_years: Optional[int] = None
    priority: str  # "obligatoire", "souhaité", "indispensable"

class JobCriteria(BaseModel):
    job_title: str
    required_skills: List[RequiredSkill] = []
    bonus_skills: List[RequiredSkill] = []
    education_level: Optional[str] = None
    min_experience: Optional[int] = None
    languages: List[Language] = []
    soft_skills: List[str] = []

class MatchItem(BaseModel):
    critere: str
    status: str # "✅", "⚠️", "❌"
    score: float
    cv: Optional[str] = None
    offre: Optional[str] = None
    note: Optional[str] = None

class MatchingResult(BaseModel):
    matches: List[MatchItem] = []
    experience_match: Dict[str, Any] = {}
    education_match: Dict[str, Any] = {}
    languages_match: Dict[str, Any] = {}
    final_score: float = 0.0
    decision: str = "" # "AUTO-ACCEPT", "HUMAN REVIEW", "WAITING LIST", "AUTO-REJECT"
    justification: str = ""

class QuestionnairePayload(BaseModel):
    candidature_id: str
    candidate_email: str
    candidate_name: str
    job_title: str
    answers: Dict[str, str]

class EvaluationResult(BaseModel):
    passed: bool
    justification: str
