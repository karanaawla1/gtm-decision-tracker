from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.attribution import analyze_decision
from app.services.cache import set_cached_analysis

@celery_app.task
def sync_all_decisions():
    """Sare active decisions ka analysis refresh karo"""
    # Models yahan import karo — Celery ke liye zaruri hai
    from app.models.decision import Decision
    from app.models.outcome import Outcome

    db = SessionLocal()
    try:
        decisions = db.query(Decision).filter(
            Decision.status == "active").all()
        updated = 0
        for decision in decisions:
            analysis = analyze_decision(decision, decision.outcomes)
            set_cached_analysis(str(decision.id), analysis)
            updated += 1
        print(f"Synced {updated} decisions")
        return {"synced": updated}
    finally:
        db.close()

@celery_app.task
def calculate_single(decision_id: str):
    """Ek decision ka analysis background mein karo"""
    from app.models.decision import Decision
    from app.models.outcome import Outcome

    db = SessionLocal()
    try:
        decision = db.query(Decision).filter(
            Decision.id == decision_id).first()
        if decision:
            analysis = analyze_decision(decision, decision.outcomes)
            set_cached_analysis(decision_id, analysis)
            return analysis
    finally:
        db.close()