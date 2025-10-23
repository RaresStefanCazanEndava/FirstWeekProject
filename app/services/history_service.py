from datetime import date
from typing import List, Dict, Any
from ..extensions import db
from ..models import Car, InsurancePolicy, Claim

def car_exists(car_id: int) -> bool:
    return db.session.get(Car, car_id) is not None

def get_history(car_id: int) -> List[Dict[str, Any]]:
    """
    Întoarce evenimentele pentru mașină în ordine cronologică ascendentă.
    POLICIES sortate după start_date, CLAIMS după claim_date.
    """
    # policies
    policies = (
        InsurancePolicy.query
        .filter(InsurancePolicy.car_id == car_id)
        .order_by(InsurancePolicy.start_date.asc(), InsurancePolicy.id.asc())
        .all()
    )
    policy_events = [{
        "type": "POLICY",
        "policyId": p.id,
        "startDate": p.start_date.isoformat(),
        "endDate": p.end_date.isoformat(),
        "provider": p.provider,
        "_sort_date": p.start_date.isoformat(),  # intern pt sortare
        "_sort_id": p.id,
    } for p in policies]

    # claims
    claims = (
        Claim.query
        .filter(Claim.car_id == car_id)
        .order_by(Claim.claim_date.asc(), Claim.id.asc())
        .all()
    )
    claim_events = [{
        "type": "CLAIM",
        "claimId": c.id,
        "claimDate": c.claim_date.isoformat(),
        "amount": float(c.amount),
        "description": c.description,
        "_sort_date": c.claim_date.isoformat(),
        "_sort_id": c.id,
    } for c in claims]

    # merge + sortare crono asc (după dată, apoi id pt stabilitate)
    events = policy_events + claim_events
    events.sort(key=lambda e: (e["_sort_date"], e["_sort_id"]))

    # elimină câmpurile interne
    for e in events:
        e.pop("_sort_date", None)
        e.pop("_sort_id", None)
    return events
