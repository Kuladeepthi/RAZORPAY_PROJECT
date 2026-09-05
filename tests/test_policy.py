"""Tests for Layer 0 & Layer 3: Reason-Code Policy and Completeness Checker."""

from src.policy.reason_code_policy import REASON_CODE_POLICY, check_completeness, get_allowed_evidence_fields


def test_known_reason_codes_exist():
    expected_codes = ["RZP00", "RZP01", "RZP02", "RZP03", "RZP04", "RZP05", "RZP06"]
    for code in expected_codes:
        assert code in REASON_CODE_POLICY, f"Missing reason code: {code}"


def test_rzp02_recurring_cancellation_completeness():
    uploaded = {"terms_and_conditions", "customer_interaction", "cancellation_policy_acknowledgement"}
    res = check_completeness("RZP02", uploaded)
    assert res["complete"] is True
    assert "refund_cancellation_policy" in res["allowed_evidence_fields"]


def test_completeness_checker_success():
    # RZP01 needs proof_of_delivery, customer_interaction, terms_and_conditions
    uploaded = {"proof_of_delivery", "customer_interaction", "terms_and_conditions"}
    res = check_completeness("RZP01", uploaded)
    assert res["complete"] is True
    assert len(res["missing"]) == 0
    assert "shipping_proof" in res["allowed_evidence_fields"] or "proof_of_service" in res["allowed_evidence_fields"]


def test_completeness_checker_missing_documents():
    uploaded = {"proof_of_delivery"}
    res = check_completeness("RZP01", uploaded)
    assert res["complete"] is False
    assert "customer_interaction" in res["missing"]
    assert "terms_and_conditions" in res["missing"]


def test_unknown_reason_code_handling():
    res = check_completeness("RZP99_INVALID", {"proof_of_delivery"})
    assert res["complete"] is False
    assert "Unknown Reason Code" in res["missing"]
