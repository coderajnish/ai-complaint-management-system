from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.complaint_model import Complaint
from schemas.complaint_schema import ComplaintCreate
from services.langgraph_workflow import app_graph
from services.ai_service import call_llm
from services.langgraph_workflow import extract_json

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze")
def analyze_complaint(payload: dict):
    result = app_graph.invoke({"raw_text": payload["text"]})

    combined = {}
    combined.update(result.get("extracted", {}))
    combined.update(result.get("risk", {}))

    required_keys = [
        "complaint_source",
        "customer_name",
        "product_name",
        "product_strength",
        "batch_number",
        "affected_quantity",
        "manufacturing_date",
        "expiry_date",
        "complaint_date",
        "originating_site",
        "impacted_materials",
        "complaint_category",
        "description",
        "structured_summary",
        "severity",
        "priority",
        "suggested_action",
        "initial_risk_assessment"
    ]

    for key in required_keys:
        if key not in combined:
            combined[key] = ""

    # Calculate completeness
    filled = []
    missing = []

    for key in required_keys:
        if combined.get(key):
            filled.append(key)
        else:
            missing.append(key)

    score = int((len(filled) / len(required_keys)) * 100)

    combined["completeness_score"] = score
    combined["missing_fields"] = missing

    return combined


@router.post("/commit")
def commit_complaint(data: ComplaintCreate, db: Session = Depends(get_db)):

    # Check for duplicate
    existing = db.query(Complaint).filter(
        Complaint.product_name == data.product_name,
        Complaint.batch_number == data.batch_number
    ).first()

    if existing:
        return {
            "duplicate": True,
            "message": "Duplicate complaint detected for this Product & Batch.",
            "existing_id": existing.id
        }

    # Save if not duplicate
    complaint = Complaint(**data.dict())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return {
        "duplicate": False,
        "message": "Complaint saved successfully.",
        "id": complaint.id
    }

from fastapi import UploadFile, File
from utils.file_parser import extract_text_from_pdf


@router.post("/analyze-pdf")
def analyze_pdf(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    result = app_graph.invoke({"raw_text": text})

    combined = {}
    combined.update(result.get("extracted", {}))
    combined.update(result.get("risk", {}))

    required_keys = [
        "complaint_source",
        "customer_name",
        "product_name",
        "product_strength",
        "batch_number",
        "affected_quantity",
        "manufacturing_date",
        "expiry_date",
        "complaint_date",
        "originating_site",
        "impacted_materials",
        "complaint_category",
        "description",
        "structured_summary",
        "severity",
        "priority",
        "suggested_action",
        "initial_risk_assessment"
    ]

    for key in required_keys:
        if key not in combined:
            combined[key] = ""

    filled = []
    missing = []

    for key in required_keys:
        if combined.get(key):
            filled.append(key)
        else:
            missing.append(key)

    score = int((len(filled) / len(required_keys)) * 100)

    combined["completeness_score"] = score
    combined["missing_fields"] = missing

    return combined

    return combined

@router.post("/modify")
def modify_complaint(payload: dict):
    current_data = payload["current_data"]
    instruction = payload["instruction"]

    prompt = f"""
You are updating a structured pharmaceutical complaint JSON.

Current JSON:
{current_data}

User instruction:
{instruction}

Return FULL updated flat JSON.
Do NOT remove any existing fields.
Return only valid JSON.
"""

    updated = call_llm(prompt)
    parsed = extract_json(updated)

    merged = current_data.copy()
    merged.update(parsed)

    return merged