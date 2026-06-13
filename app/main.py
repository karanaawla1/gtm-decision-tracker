from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import decision, outcome
from app.api import decisions
from app.api import outcomes as outcomes_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GTM Decision Tracker",
    description="Track ROI of GTM decisions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(outcomes_router.router, prefix="/api/outcomes", tags=["Outcomes"])

@app.get("/")
def root():
    return {"message": "GTM Tracker chal raha hai!"}