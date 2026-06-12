import pandas as pd
from sqlalchemy.orm import Session
from app.models.decision import Decision

VALID_TYPES = ["hire", "ad_spend", "vendor", "tool"]

def validate_row(row):
    if row["type"] not in VALID_TYPES:
        raise ValueError(f"Invalid type: {row['type']}")
    if float(row["cost_amount"]) <= 0:
        raise ValueError("Cost must be positive")
    return True

def process_csv_file(file_path: str, db: Session):
    # Extract
    df = pd.read_csv(file_path)

    # Transform
    df["date"] = pd.to_datetime(df["date"])
    df["cost_amount"] = pd.to_numeric(df["cost_amount"], errors="coerce")
    df = df.dropna(subset=["type", "cost_amount"])
    df = df.fillna({"description": "No description", "owner": "Unknown"})

    results = {"success": 0, "failed": 0, "errors": []}

    # Load
    for _, row in df.iterrows():
        try:
            validate_row(row)
            decision = Decision(
                type=row["type"],
                date=row["date"].to_pydatetime(),
                owner=str(row["owner"]),
                cost_amount=float(row["cost_amount"]),
                description=str(row["description"]),
            )
            db.add(decision)
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(str(e))

    db.commit()
    return results