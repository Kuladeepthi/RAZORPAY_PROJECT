"""
SentinelEvidence — Layer 4: Cost-Calibrated Decision Gate

Combines forensic tamper score, content consistency score, and reason-code completeness
into an actionable business decision:
1. ACCEPT -> Routed to Agentic Drafter (Clean evidence, matches ledger)
2. ABSTAIN -> Routed to Human Review Queue (Ambiguous confidence or missing documentation)
3. REJECT -> Flagged as Fraudulent Evidence (Confirmed tamper or ledger discrepancy)

Includes explicit Rupee Loss Cost Calibration:
- False REJECT: Merchant payout delay & friction penalty
- False ACCEPT: Full financial chargeback forfeiture to fraudulent claim
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class DecisionOutcome(str, Enum):
    ACCEPT = "ACCEPT"
    ABSTAIN = "ABSTAIN"
    REJECT = "REJECT"


class GateDecision(BaseModel):
    decision: DecisionOutcome
    tamper_score: float
    consistency_score: float
    is_complete: bool
    reasons: List[str]
    suggested_action: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    dispute_amount_inr: float = 0.0


def compute_expected_rupee_loss(
    y_true_tampered: List[int],
    y_pred_tamper_score: List[float],
    transaction_amounts: List[float],
    threshold_reject: float = 0.65,
    threshold_accept: float = 0.35,
    cost_false_reject_base: float = 250.0,  # Illustrative Assumption: ₹250 estimated merchant dispute ticket escalation & delay cost
    cost_abstain_triage: float = 50.0,      # Illustrative Assumption: ₹50 estimated human triage handling & ops reviewer cost
) -> Dict[str, float]:
    """
    Computes real financial Rupee impact across the decision threshold spectrum.
    
    Unit-Cost Framework:
    - False REJECT (Genuine document falsely blocked): Operational friction & merchant support cost (Assumed ~₹250)
    - False ACCEPT (Forged evidence silently passed): Full transaction chargeback forfeiture (₹ Dispute Amount)
    - ABSTAIN (Ambiguous evidence deferred): Human ops triage review cost (Assumed ~₹50)
    
    Note: These baseline unit costs are illustrative operational benchmarks; in a live deployment,
    they are calibrated dynamically against Razorpay merchant tiering and SLA agreements.
    """
    total_loss = 0.0
    fp_count = 0
    fn_count = 0
    abstain_count = 0

    for y_true, score, amt in zip(y_true_tampered, y_pred_tamper_score, transaction_amounts):
        if score > threshold_reject:
            # Model says REJECT
            if y_true == 0:
                # Genuine doc wrongly rejected (False Positive)
                loss = cost_false_reject_base + (0.02 * amt)
                total_loss += loss
                fp_count += 1
        elif score < threshold_accept:
            # Model says ACCEPT
            if y_true == 1:
                # Tampered doc wrongly passed (False Negative)
                loss = amt  # 100% dispute loss
                total_loss += loss
                fn_count += 1
        else:
            # Model ABSTAINS -> Human Review
            total_loss += 50.0  # ₹50 operational review cost
            abstain_count += 1

    return {
        "total_rupee_loss": round(total_loss, 2),
        "false_rejections_count": fp_count,
        "false_acceptances_count": fn_count,
        "abstentions_count": abstain_count,
        "average_loss_per_case": round(total_loss / max(1, len(y_true_tampered)), 2),
    }


def evaluate_decision_gate(
    tamper_score: float,
    consistency_score: float,
    completeness_result: Dict[str, Any],
    dispute_amount: float = 0.0,
    threshold_accept: float = 0.35,
    threshold_reject: float = 0.65
) -> GateDecision:
    """
    Evaluates multi-signal inputs against the cost-calibrated decision boundary.
    """
    is_complete = completeness_result.get("complete", False)
    missing_docs = completeness_result.get("missing", [])
    reasons = []

    # 1. Check completeness first (Layer 3)
    if not is_complete:
        reasons.append(f"Incomplete submission: Missing mandatory document(s): {', '.join(missing_docs)}")
        return GateDecision(
            decision=DecisionOutcome.ABSTAIN,
            tamper_score=tamper_score,
            consistency_score=consistency_score,
            is_complete=False,
            reasons=reasons,
            suggested_action="Route to Merchant Portal: Request missing evidence documents.",
            risk_level="MEDIUM",
            dispute_amount_inr=dispute_amount
        )

    # 2. Check for confirmed fraud / tampering (REJECT)
    if tamper_score >= threshold_reject:
        reasons.append(f"High digital tamper probability ({tamper_score:.2f} >= {threshold_reject:.2f})")
    if consistency_score <= 0.30:
        reasons.append(f"Severe ledger inconsistency ({consistency_score:.2f} <= 0.30)")

    if reasons:
        return GateDecision(
            decision=DecisionOutcome.REJECT,
            tamper_score=tamper_score,
            consistency_score=consistency_score,
            is_complete=True,
            reasons=reasons,
            suggested_action="Block representment: Flag evidence as fraudulent and notify merchant risk team.",
            risk_level="CRITICAL" if tamper_score > 0.8 else "HIGH",
            dispute_amount_inr=dispute_amount
        )

    # 3. Check for clear genuine clearance (ACCEPT)
    if tamper_score < threshold_accept and consistency_score >= 0.70:
        return GateDecision(
            decision=DecisionOutcome.ACCEPT,
            tamper_score=tamper_score,
            consistency_score=consistency_score,
            is_complete=True,
            reasons=["Evidence authenticated: low tamper variance and perfect ledger reconciliation."],
            suggested_action="Proceed to Auto-Draft: Compile Visa/Mastercard dispute contestation packet.",
            risk_level="LOW",
            dispute_amount_inr=dispute_amount
        )

    # 4. Ambiguous Middle Band (ABSTAIN) -> Graceful Escalation
    ambiguous_details = []
    if threshold_accept <= tamper_score < threshold_reject:
        ambiguous_details.append(f"Borderline forensic confidence ({tamper_score:.2f})")
    if 0.30 < consistency_score < 0.70:
        ambiguous_details.append(f"Partial ledger entity match ({consistency_score:.2f})")

    return GateDecision(
        decision=DecisionOutcome.ABSTAIN,
        tamper_score=tamper_score,
        consistency_score=consistency_score,
        is_complete=True,
        reasons=ambiguous_details or ["Forensic signals land in ambiguous confidence corridor."],
        suggested_action="Escalate to Human Dispute Analyst: Secondary manual inspection required.",
        risk_level="MEDIUM",
        dispute_amount_inr=dispute_amount
    )
