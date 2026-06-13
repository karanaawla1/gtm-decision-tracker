import pandas as pd
from sqlalchemy.orm import Session
from app.models.decision import Decision

ALLOWED_TYPES = ["hire", "ad_spend", "vendor", "tool"]

def check_row(row):
    if row["type"] not in ALLOWED_TYPES:
        raise ValueError(f"Type galat hai: {row['type']}")
    if float(row["cost_amount"]) <= 0:
        raise ValueError("Cost zero ya negative nahi ho sakta")
    return True

def process_csv_file(file_path: str, db: Session):
    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["date"])
    df["cost_amount"] = pd.to_numeric(df["cost_amount"], errors="coerce")
    df = df.dropna(subset=["type", "cost_amount"])
    df = df.fillna({"description": "", "owner": "Unknown"})

    stats = {"success": 0, "failed": 0, "errors": []}

    for _, row in df.iterrows():
        try:
            check_row(row)
            entry = Decision(
                type=row["type"],
                date=row["date"].to_pydatetime(),
                owner=str(row["owner"]),
                cost_amount=float(row["cost_amount"]),
                description=str(row["description"]),
            )
            db.add(entry)
            stats["success"] += 1
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(str(e))

    db.commit()
    return stats