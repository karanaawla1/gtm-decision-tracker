from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

app.mount("/static",StaticFiles(directory="app/static"), name="statice")

app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(outcomes_router.router, prefix="/api/outcomes", tags=["Outcomes"])

@app.get("/")
def root():
    return FileResponse("app/static/index.html")