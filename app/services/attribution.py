import math
def get_outcome_weight(decision_date, outcome_date, decay=0.02):
    day_gap = (outcome_date - decision_date).days
    
    if day_gap < 0 or day_gap > 90:
        return 0.0
    return math.exp(-decay * day_gap)

def get_roi(decision, outcomes):
    weighted_revenue = 0
    total_weight = 0    
    for outcome in outcomes:
        w = get_outcome_weight(decision.date, outcome.date)
        if w > 0:
            weighted_revenue += outcome.value * w
            total_weight += w
    if total_weight == 0 or decision.cost_amount == 0:
        return 0.0
    return round((weighted_revenue / total_weight) / decision.cost_amount, 2)
def get_confidence(outcomes, decision_date):
    # sirf relevant outcomes lo
    valid = [o for o in outcomes if get_outcome_weight(decision_date, o.date) > 0]
    
    if not valid:
        return 0.0
    data_score = min(len(valid) / 10, 1.0)
    if len(valid) > 1:
        values = [o.value for o in valid]
        avg = sum(values) / len(values)
        std_dev = (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5
        consistency = max(0, 1 - (std_dev / avg if avg else 1))
    else:
        consistency = 0.5  
    return round(min(data_score * 0.6 + consistency * 0.4, 1.0), 2)
def decide(roi, confidence):
    if roi > 3.0 and confidence > 0.7:
        return "SCALE"      
    elif roi < 0.5 and confidence > 0.6:
        return "KILL"       
    elif confidence < 0.6:
        return "MONITOR"    
    return "MAINTAIN"       

def analyze_decision(decision, outcomes):
    roi = get_roi(decision, outcomes)
    confidence = get_confidence(outcomes, decision_date=decision.date)
    
    return {
        "decision_id": str(decision.id),
        "roi": roi,
        "confidence": confidence,
        "recommendation": decide(roi, confidence),
        "outcomes_count": len(outcomes)
    }