import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum("hire", "ad_spend", "vendor", "tool", name="decision_type"))
    date = Column(DateTime, default=datetime.utcnow)
    owner = Column(String(100))
    cost_amount = Column(Float, nullable=False)
    description = Column(String(500))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Ek decision ke kai outcomes ho sakte hain
    outcomes = relationship("Outcome", back_populates="decision")