from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.outcome import Outcome

router = APIRouter()

class OutcomeCreate(BaseModel):
    decision_id: str
    metric_type: str
    value: float
    source: Optional[str] = "manual"
    date: Optional[datetime] = None

@router.post("/")
def add_outcome(data: OutcomeCreate, db: Session = Depends(get_db)):
    new_outcome = Outcome(
        decision_id=data.decision_id,
        metric_type=data.metric_type,
        value=data.value,
        source=data.source,
        date=data.date or datetime.utcnow()
    )
    db.add(new_outcome)
    db.commit()
    db.refresh(new_outcome)
    return {"message": "Outcome saved!", "id": str(new_outcome.id)}

@router.get("/{decision_id}")
def fetch_outcomes(decision_id: str, db: Session = Depends(get_db)):
    return db.query(Outcome).filter(Outcome.decision_id == decision_id).all()