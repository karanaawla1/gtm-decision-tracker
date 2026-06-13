from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.attribution import analyze_decision
from app.services.cache import set_cached_analysis

@celery_app.task
def refresh_all_decisions():
    from app.models.decision import Decision

    db = SessionLocal()
    try:
        active = db.query(Decision).filter(Decision.status == "active").all()
        count = 0
        for d in active:
            result = analyze_decision(d, d.outcomes)
            set_cached_analysis(str(d.id), result)
            count += 1
        print(f"{count} decisions refresh ho gaye")
        return {"refreshed": count}
    finally:
        db.close()

@celery_app.task
def refresh_single(decision_id: str):
    from app.models.decision import Decision

    db = SessionLocal()
    try:
        d = db.query(Decision).filter(Decision.id == decision_id).first()
        if d:
            result = analyze_decision(d, d.outcomes)
            set_cached_analysis(decision_id, result)
            return result
    finally:
        db.close()