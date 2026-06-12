import math

def time_decay_weight(decision_date, outcome_date, lambda_val=0.02):
    days_diff = (outcome_date - decision_date).days
    if days_diff < 0 or days_diff > 90:
        return 0.0
    return math.exp(-lambda_val * days_diff)

def calculate_weighted_roi(decision, outcomes):
    total_weighted_revenue = 0
    total_weight = 0
    for outcome in outcomes:
        weight = time_decay_weight(decision.date, outcome.date)
        if weight > 0:
            total_weighted_revenue += outcome.value * weight
            total_weight += weight
    if total_weight == 0 or decision.cost_amount == 0:
        return 0.0
    return round((total_weighted_revenue / total_weight) / decision.cost_amount, 2)

def calculate_confidence(outcomes, decision_date):
    relevant = [o for o in outcomes
                if time_decay_weight(decision_date, o.date) > 0]
    if not relevant:
        return 0.0
    data_conf = min(len(relevant) / 10, 1.0)
    if len(relevant) > 1:
        vals = [o.value for o in relevant]
        mean = sum(vals) / len(vals)
        std = (sum((v-mean)**2 for v in vals)/len(vals))**0.5
        consistency = max(0, 1-(std/mean if mean else 1))
    else:
        consistency = 0.5
    return round(min(data_conf*0.6 + consistency*0.4, 1.0), 2)

def get_recommendation(roi, confidence):
    if roi > 3.0 and confidence > 0.7:
        return "SCALE"
    elif roi < 0.5 and confidence > 0.6:
        return "KILL"
    elif confidence < 0.6:
        return "MONITOR"
    return "MAINTAIN"

def analyze_decision(decision, outcomes):
    roi = calculate_weighted_roi(decision, outcomes)
    confidence = calculate_confidence(outcomes, decision.date)
    return {
        "decision_id": str(decision.id),
        "roi": roi,
        "confidence": confidence,
        "recommendation": get_recommendation(roi, confidence),
        "outcomes_count": len(outcomes)
    }