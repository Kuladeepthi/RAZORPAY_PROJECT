"""
SentinelEvidence — Layer 0 & Layer 3: Reason-Code Policy Engine

Built directly from Razorpay's public dispute evidence guidelines:
https://razorpay.com/docs/payments/disputes/submit-evidence

Given a dispute's reason_code (RZP00-RZP06), this provides:
1. Which evidence categories are mandatory before an auto-response is considered.
2. Which specific fields of Razorpay's Dispute `evidence{}` object can be populated.
3. Explicit verification that incomplete cases are short-circuited with actionable diagnostics.
"""

from typing import Dict, List, Set, Any, Optional

REASON_CODE_POLICY: Dict[str, Dict[str, Any]] = {
    "RZP00": {
        "name": "General / Uncategorized",
        "description": "Dispute not available or doesn't fit standard chargeback categories.",
        "required_evidence": [
            "proof_of_delivery",
            "invoice_details",
            "customer_email_communication",
            "refund_details_if_applicable",
        ],
        "evidence_fields": [
            "proof_of_service",
            "explanation_letter",
            "customer_communication",
            "refund_confirmation",
        ],
        "risk_weight": 1.0,
    },
    "RZP01": {
        "name": "Goods/Services Not Provided",
        "description": "Customer claims service or physical goods were not received.",
        "required_evidence": [
            "proof_of_delivery",
            "customer_interaction",
            "terms_and_conditions",
        ],
        "evidence_fields": [
            "proof_of_service",
            "shipping_proof",
            "customer_communication",
            "term_and_conditions",
            "explanation_letter",
        ],
        "risk_weight": 1.2,
    },
    "RZP02": {
        "name": "Cancelled Recurring Transaction",
        "description": "Customer claims recurring billing or subscription was charged after cancellation.",
        "required_evidence": [
            "terms_and_conditions",
            "customer_interaction",
            "cancellation_policy_acknowledgement",
        ],
        "evidence_fields": [
            "refund_cancellation_policy",
            "term_and_conditions",
            "customer_communication",
            "access_activity_log",
            "explanation_letter",
        ],
        "risk_weight": 1.0,
    },
    "RZP03": {
        "name": "Defective / Not as Described",
        "description": "Customer claims goods received were damaged, counterfeit, or misrepresented.",
        "required_evidence": [
            "product_specification_sheet",
            "customer_interaction",
            "return_policy",
        ],
        "evidence_fields": [
            "billing_proof",
            "proof_of_service",
            "customer_communication",
            "refund_cancellation_policy",
            "explanation_letter",
        ],
        "risk_weight": 1.1,
    },
    "RZP04": {
        "name": "Refund Not Processed",
        "description": "Customer claims agreed refund was never credited to bank account.",
        "required_evidence": [
            "refund_generation_proof",
            "bank_statement_matching_amount",
            "refund_confirmation_communication",
            "refund_policy",
        ],
        "evidence_fields": [
            "refund_confirmation",
            "customer_communication",
            "refund_cancellation_policy",
            "explanation_letter",
        ],
        "risk_weight": 0.9,
    },
    "RZP05": {
        "name": "Account Debited Without Confirmation",
        "description": "Customer bank debited but order status failed/unconfirmed in merchant system.",
        "required_evidence": [
            "invoice_if_captured",
            "internal_logs_if_failed",
            "customer_interaction",
            "terms_and_conditions",
        ],
        "evidence_fields": [
            "proof_of_service",
            "billing_proof",
            "access_activity_log",
            "customer_communication",
            "term_and_conditions",
            "explanation_letter",
        ],
        "risk_weight": 1.1,
    },
    "RZP06": {
        "name": "Business Not Responding",
        "description": "Customer claims merchant failed to respond to support inquiries.",
        "required_evidence": [
            "proof_of_delivery_within_committed_timeline",
            "invoicing_details",
            "customer_email_communication",
        ],
        "evidence_fields": [
            "proof_of_service",
            "shipping_proof",
            "explanation_letter",
            "customer_communication",
        ],
        "risk_weight": 1.0,
    },
}


def check_completeness(reason_code: str, uploaded_evidence_types: Set[str]) -> Dict[str, Any]:
    """
    Evaluates whether the submitted set of evidence documents meets Razorpay's mandatory requirements.

    Args:
        reason_code: Razorpay reason code (e.g. 'RZP01').
        uploaded_evidence_types: Set of classified document types (e.g. {'proof_of_delivery', 'terms_and_conditions'}).

    Returns:
        Dict containing completeness boolean, missing required items, allowed schema fields, and diagnostic message.
    """
    normalized_code = reason_code.upper().strip()
    policy = REASON_CODE_POLICY.get(normalized_code)
    
    if policy is None:
        return {
            "complete": False,
            "missing": ["Unknown Reason Code"],
            "allowed_evidence_fields": [],
            "policy": None,
            "diagnostic": f"Unrecognized Razorpay reason code: '{reason_code}'."
        }

    # Normalize category names
    uploaded_clean = {t.lower().strip() for t in uploaded_evidence_types}
    required = set(policy["required_evidence"])
    
    # Fuzzy category normalization for seamless merchant upload matching
    matched_required = set()
    for req in required:
        for up in uploaded_clean:
            if req in up or up in req or req.replace("_", "") in up.replace("_", ""):
                matched_required.add(req)
                break
                
    missing = sorted(list(required - matched_required))
    is_complete = len(missing) == 0

    return {
        "complete": is_complete,
        "missing": missing,
        "allowed_evidence_fields": policy["evidence_fields"],
        "policy": policy,
        "diagnostic": "All required evidence present." if is_complete else f"Missing required evidence for {normalized_code}: {', '.join(missing)}."
    }


def get_allowed_evidence_fields(reason_code: str) -> List[str]:
    """Returns the whitelisted Razorpay evidence object fields for a given reason code."""
    policy = REASON_CODE_POLICY.get(reason_code.upper().strip())
    return policy["evidence_fields"] if policy else ["explanation_letter", "others"]
