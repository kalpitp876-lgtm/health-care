"""Deterministic, deliberately limited triage and specialist mapping tools.

This is an educational demonstration, not a clinically validated triage protocol.
Never use this mapping to rule out emergencies or delay professional care.
"""
from typing import Literal
from langchain_core.tools import tool

# These are illustrative keyword rules, not a complete clinical decision system.
# Emergency keywords are intentionally conservative. This is not exhaustive.
URGENT_TERMS = (
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "severe shortness of breath", "face drooping", "slurred speech",
    "weakness on one side", "uncontrolled bleeding", "seizure",
    "suicidal", "overdose", "anaphylaxis", "throat closing",
)
DOCTOR_TERMS = (
    "fever", "headache", "migraine", "rash", "vomiting", "diarrhea",
    "stomach pain", "abdominal pain", "ear pain", "sore throat",
    "persistent cough", "urinary pain", "painful urination", "joint pain",
)

def classify_triage(text: str) -> dict:
    """Return a deterministic triage level using a small explicit keyword table."""
    normalized = " ".join((text or "").lower().strip().split())
    if not normalized:
        return {
            "triage_level": "uncertain",
            "reason": "No symptom text was provided.",
            "next_step": "Please describe the concern. If you think this may be an emergency, contact local emergency services now.",
        }

    matched_urgent = [term for term in URGENT_TERMS if term in normalized]
    if matched_urgent:
        return {
            "triage_level": "urgent",
            "matched_rule": matched_urgent,
            "reason": "The text contains a keyword in this prototype's emergency-warning list.",
            "next_step": "Seek emergency medical help now or contact your local emergency number. Do not wait for this app.",
        }

    matched_doctor = [term for term in DOCTOR_TERMS if term in normalized]
    if matched_doctor:
        return {
            "triage_level": "see a doctor",
            "matched_rule": matched_doctor,
            "reason": "The text matches a symptom in this prototype's clinician-review list.",
            "next_step": "Arrange medical advice from a qualified clinician. Seek urgent help if symptoms are severe, worsening, or concerning.",
        }

    return {
        "triage_level": "uncertain",
        "matched_rule": [],
        "reason": "No rule matched. This prototype cannot safely classify every symptom or medication concern.",
        "next_step": "Contact a qualified healthcare professional for guidance. If symptoms are severe, rapidly worsening, or you suspect an emergency, seek urgent help.",
    }

SPECIALIST_RULES = {
    "chest pain": ("Emergency department / emergency services", "urgent"),
    "difficulty breathing": ("Emergency department / emergency services", "urgent"),
    "can't breathe": ("Emergency department / emergency services", "urgent"),
    "cannot breathe": ("Emergency department / emergency services", "urgent"),
    "face drooping": ("Emergency department / emergency services", "urgent"),
    "slurred speech": ("Emergency department / emergency services", "urgent"),
    "headache": ("Primary care clinician; emergency department for sudden severe headache or neurological warning signs", "routine unless severe or warning signs are present"),
    "migraine": ("Primary care clinician; neurology may be appropriate for recurrent or complex migraine", "routine unless severe or warning signs are present"),
    "rash": ("Primary care clinician or dermatologist; emergency services for breathing difficulty or facial/throat swelling", "depends on severity"),
    "fever": ("Primary care clinician; urgent care for severe symptoms or high-risk situations", "depends on severity"),
    "stomach pain": ("Primary care clinician; emergency department for severe or worsening pain", "depends on severity"),
    "abdominal pain": ("Primary care clinician; emergency department for severe or worsening pain", "depends on severity"),
    "persistent cough": ("Primary care clinician; respiratory specialist if referred", "routine unless breathing difficulty or severe symptoms"),
    "joint pain": ("Primary care clinician; rheumatology or orthopedics if referred", "routine unless severe injury or warning signs"),
}

def find_specialist(condition: str, triage_level: str = "uncertain") -> dict:
    """Map symptom text and triage result to a suggested clinician/department."""
    normalized = " ".join((condition or "").lower().strip().split())
    if triage_level == "urgent":
        return {
            "specialist_or_department": "Emergency department / local emergency services",
            "urgency": "urgent",
            "reason": "The deterministic triage result is urgent.",
        }
    for phrase, (department, urgency) in SPECIALIST_RULES.items():
        if phrase in normalized:
            return {
                "specialist_or_department": department,
                "urgency": urgency,
                "reason": f"Matched the explicit specialist mapping for '{phrase}'.",
            }
    return {
        "specialist_or_department": "Primary care clinician / qualified healthcare professional",
        "urgency": "uncertain; seek urgent care if severe or worsening",
        "reason": "No specific specialist mapping matched; a primary care clinician can assess and refer if needed.",
    }

@tool
def symptom_triage(symptom_or_condition: str) -> str:
    """Classify a symptom using explicit Python keyword rules. Input is the patient's symptom text. Returns urgent, see a doctor, or uncertain plus a safe next step. This is a limited demo, not clinical advice."""
    import json
    return json.dumps(classify_triage(symptom_or_condition), ensure_ascii=False)

@tool
def specialist_finder(condition: str, triage_level: str = "uncertain") -> str:
    """Suggest a clinician or department from a fixed Python lookup table. Use the symptom/condition and the deterministic triage result. Not a diagnosis."""
    import json
    return json.dumps(find_specialist(condition, triage_level), ensure_ascii=False)
