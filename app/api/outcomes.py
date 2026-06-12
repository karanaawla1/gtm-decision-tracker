from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.outcome import Outcome

router = APIRouter()

class OutcomeCreate(BaseModel):
    decision_id: str
    metric_type: str    # revenue, pipeline, churn
    value: float
    source: Optional[str] = "manual"
    date: Optional[datetime] = None

@router.post("/")
def create_outcome(data: OutcomeCreate, db: Session = Depends(get_db)):
    outcome = Outcome(
        decision_id=data.decision_id,
        metric_type=data.metric_type,
        value=data.value,
        source=data.source,
        date=data.date or datetime.utcnow()
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return {"message": "Outcome created!", "id": str(outcome.id)}

@router.get("/{decision_id}")
def get_outcomes(decision_id: str, db: Session = Depends(get_db)):
    outcomes = db.query(Outcome).filter(
        Outcome.decision_id == decision_id).all()
    return outcomes