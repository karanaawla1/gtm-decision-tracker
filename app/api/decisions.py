from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import tempfile, os
from app.database import get_db
from app.models.decision import Decision
from app.models.outcome import Outcome
from app.services.attribution import analyze_decision
from app.services.cache import get_cached_analysis, set_cached_analysis, invalidate_cache

router = APIRouter()

class NewDecision(BaseModel):
    type: str
    owner: str
    cost_amount: float
    description: Optional[str] = ""
    date: Optional[datetime] = None

class EditDecision(BaseModel):
    type: Optional[str] = None
    owner: Optional[str] = None
    cost_amount: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None

@router.post("/")
def add_decision(data: NewDecision, db: Session = Depends(get_db)):
    entry = Decision(
        type=data.type,
        owner=data.owner,
        cost_amount=data.cost_amount,
        description=data.description,
        date=data.date or datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"message": "Decision saved!", "id": str(entry.id)}

@router.get("/")
def list_decisions(db: Session = Depends(get_db)):
    all_decisions = db.query(Decision).all()
    return [
        {
            "id": str(d.id),
            "type": d.type,
            "owner": d.owner,
            "cost_amount": d.cost_amount,
            "description": d.description,
            "status": d.status,
            "date": d.date
        }
        for d in all_decisions
    ]

@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    all_decisions = db.query(Decision).all()

    total_cost = sum(d.cost_amount for d in all_decisions)
    rec_counts = {"SCALE": 0, "KILL": 0, "MONITOR": 0, "MAINTAIN": 0, "NO_DATA": 0}
    total_roi = 0
    roi_count = 0

    for d in all_decisions:
        if d.outcomes:
            # Pehle cache check karo, nahi mile to directly calculate karo
            cached = get_cached_analysis(str(d.id))
            if cached:
                analysis = cached
            else:
                analysis = analyze_decision(d, d.outcomes)
                set_cached_analysis(str(d.id), analysis)

            rec = analysis.get("recommendation", "NO_DATA")
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
            total_roi += analysis.get("roi", 0)
            roi_count += 1
        else:
            rec_counts["NO_DATA"] += 1

    type_breakdown = {}
    for d in all_decisions:
        type_breakdown[d.type] = type_breakdown.get(d.type, 0) + 1

    return {
        "total_decisions": len(all_decisions),
        "total_investment": round(total_cost, 2),
        "average_roi": round(total_roi / roi_count, 2) if roi_count > 0 else 0,
        "recommendations": rec_counts,
        "type_breakdown": type_breakdown,
    }

@router.get("/bulk-analysis")
def all_decisions_roi(db: Session = Depends(get_db)):
    all_decisions = db.query(Decision).all()
    results = []

    for d in all_decisions:
        cached = get_cached_analysis(str(d.id))
        if cached:
            cached["from_cache"] = True
            cached["decision_type"] = d.type
            cached["owner"] = d.owner
            results.append(cached)
            continue

        if d.outcomes:
            analysis = analyze_decision(d, d.outcomes)
            set_cached_analysis(str(d.id), analysis)
            analysis["from_cache"] = False
            analysis["decision_type"] = d.type
            analysis["owner"] = d.owner
            results.append(analysis)
        else:
            results.append({
                "decision_id": str(d.id),
                "decision_type": d.type,
                "owner": d.owner,
                "roi": 0,
                "confidence": 0,
                "recommendation": "NO_DATA",
                "outcomes_count": 0,
                "from_cache": False
            })

    return {"total": len(results), "analyses": results}

@router.get("/{decision_id}/analysis")
def run_analysis(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, detail="Decision nahi mila!")

    cached = get_cached_analysis(decision_id)
    if cached:
        cached["from_cache"] = True
        return cached

    result = analyze_decision(d, d.outcomes)
    set_cached_analysis(decision_id, result)
    result["from_cache"] = False
    return result

@router.patch("/{decision_id}")
def edit_decision(decision_id: str, data: EditDecision, db: Session = Depends(get_db)):
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, detail="Decision nahi mila!")

    if data.type is not None: d.type = data.type
    if data.owner is not None: d.owner = data.owner
    if data.cost_amount is not None: d.cost_amount = data.cost_amount
    if data.description is not None: d.description = data.description
    if data.status is not None: d.status = data.status

    db.commit()
    db.refresh(d)
    invalidate_cache(decision_id)
    return {"message": "Decision updated!", "id": decision_id}

@router.delete("/{decision_id}")
def remove_decision(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(Decision).filter(Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, detail="Decision nahi mila!")

    db.query(Outcome).filter(Outcome.decision_id == decision_id).delete()
    db.delete(d)
    db.commit()
    invalidate_cache(decision_id)
    return {"message": "Decision removed!"}

@router.post("/upload-csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, detail="Sirf CSV allowed hai!")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        from app.pipelines.csv_pipeline import process_csv_file
        result = process_csv_file(tmp_path, db)
        return {"message": "Import done!", "result": result}
    finally:
        os.unlink(tmp_path)