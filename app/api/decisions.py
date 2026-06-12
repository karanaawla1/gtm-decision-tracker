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

# ─── Pydantic Models ──────────────────────────────────────
class DecisionCreate(BaseModel):
    type: str
    owner: str
    cost_amount: float
    description: Optional[str] = ""
    date: Optional[datetime] = None

class DecisionUpdate(BaseModel):
    type: Optional[str] = None
    owner: Optional[str] = None
    cost_amount: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None

# ─── POST /api/decisions/ ─────────────────────────────────
@router.post("/")
def create_decision(data: DecisionCreate, db: Session = Depends(get_db)):
    decision = Decision(
        type=data.type,
        owner=data.owner,
        cost_amount=data.cost_amount,
        description=data.description,
        date=data.date or datetime.utcnow()
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return {"message": "Decision created!", "id": str(decision.id)}

# ─── GET /api/decisions/ ──────────────────────────────────
@router.get("/")
def get_decisions(db: Session = Depends(get_db)):
    decisions = db.query(Decision).all()
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
        for d in decisions
    ]

# ─── GET /api/decisions/summary ───────────────────────────
# Dashboard ke liye — ek call mein sab stats
@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    decisions = db.query(Decision).all()
    
    total_cost = sum(d.cost_amount for d in decisions)
    
    rec_counts = {"SCALE": 0, "KILL": 0, "MONITOR": 0, "MAINTAIN": 0, "NO_DATA": 0}
    total_roi = 0
    roi_count = 0
    
    for d in decisions:
        cached = get_cached_analysis(str(d.id))
        if cached:
            rec = cached.get("recommendation", "NO_DATA")
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
            total_roi += cached.get("roi", 0)
            roi_count += 1
    
    avg_roi = round(total_roi / roi_count, 2) if roi_count > 0 else 0
    
    type_breakdown = {}
    for d in decisions:
        type_breakdown[d.type] = type_breakdown.get(d.type, 0) + 1
    
    return {
        "total_decisions": len(decisions),
        "total_investment": round(total_cost, 2),
        "average_roi": avg_roi,
        "recommendations": rec_counts,
        "type_breakdown": type_breakdown,
    }

# ─── GET /api/decisions/bulk-analysis ─────────────────────
# Sab decisions ka ROI ek saath
@router.get("/bulk-analysis")
def bulk_analysis(db: Session = Depends(get_db)):
    decisions = db.query(Decision).all()
    results = []
    
    for d in decisions:
        # Pehle cache check karo
        cached = get_cached_analysis(str(d.id))
        if cached:
            cached["from_cache"] = True
            cached["decision_type"] = d.type
            cached["owner"] = d.owner
            results.append(cached)
            continue
        
        # Cache miss — calculate karo
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
    
    return {
        "total": len(results),
        "analyses": results
    }

# ─── GET /api/decisions/{id}/analysis ────────────────────
@router.get("/{decision_id}/analysis")
def get_analysis(decision_id: str, db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(
        Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(404, detail="Decision nahi mila!")

    cached = get_cached_analysis(decision_id)
    if cached:
        cached["from_cache"] = True
        return cached

    result = analyze_decision(decision, decision.outcomes)
    set_cached_analysis(decision_id, result)
    result["from_cache"] = False
    return result

# ─── PATCH /api/decisions/{id} ───────────────────────────
# Decision update karo
@router.patch("/{decision_id}")
def update_decision(
    decision_id: str,
    data: DecisionUpdate,
    db: Session = Depends(get_db)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(404, detail="Decision nahi mila!")

    # Sirf jo fields aaye unhe update karo
    if data.type is not None:
        decision.type = data.type
    if data.owner is not None:
        decision.owner = data.owner
    if data.cost_amount is not None:
        decision.cost_amount = data.cost_amount
    if data.description is not None:
        decision.description = data.description
    if data.status is not None:
        decision.status = data.status

    db.commit()
    db.refresh(decision)
    
    # Cache invalidate karo — data change ho gaya
    invalidate_cache(decision_id)
    
    return {"message": "Decision updated!", "id": decision_id}

# ─── DELETE /api/decisions/{id} ──────────────────────────
@router.delete("/{decision_id}")
def delete_decision(decision_id: str, db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(
        Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(404, detail="Decision nahi mila!")

    # Pehle related outcomes delete karo
    db.query(Outcome).filter(
        Outcome.decision_id == decision_id).delete()
    
    # Phir decision delete karo
    db.delete(decision)
    db.commit()
    
    # Cache bhi clear karo
    invalidate_cache(decision_id)
    
    return {"message": "Decision delete ho gaya!"}

# ─── POST /api/decisions/upload-csv ──────────────────────
@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, detail="Sirf CSV files allowed hain!")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from app.pipelines.csv_pipeline import process_csv_file
        result = process_csv_file(tmp_path, db)
        return {"message": "Upload successful!", "result": result}
    finally:
        os.unlink(tmp_path)