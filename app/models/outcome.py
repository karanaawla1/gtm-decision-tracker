import uuid
from datetime import datetime
from sqlalchemy import Column, Float, DateTime, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Outcome(Base):
    __tablename__ = "outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"))
    metric_type = Column(Enum("revenue", "pipeline", "churn", name="metric_type"))
    value = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=0.5)
    source = Column(String(50), default="manual")

    # Outcome apne decision ko jaanta hai
    decision = relationship("Decision", back_populates="outcomes")