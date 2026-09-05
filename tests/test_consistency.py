"""Tests for Layer 2: OCR Entity Extraction and Mock Ledger Reconciliation."""

from src.consistency.models import EvidenceMetadata
from src.consistency.ocr_engine import parse_entities_from_text
from src.consistency.ledger_matcher import MockRazorpayLedger, evaluate_evidence_consistency


def test_regex_entity_parser():
    sample_ocr = "Invoice: INV-2026-8942 Total Amount: ₹ 12,499.00 Payment Ref: pay_N9vKl4M29Lp1 Date: 18-Aug-2026"
    entities = parse_entities_from_text(sample_ocr)
    assert entities["extracted_amount"] == 12499.00
    assert entities["extracted_txn_id"] == "pay_N9vKl4M29Lp1"
    assert entities["extracted_date"] == "18-Aug-2026"


def test_ledger_reconciliation_match():
    ledger = MockRazorpayLedger()
    meta = EvidenceMetadata(
        document_id="doc_test_01",
        document_type="invoice_details",
        extracted_amount=4850.00,
        extracted_txn_id="pay_N9vKl4M29Lp1",
        extracted_order_id="order_N8xKm92Lp01"
    )
    report = evaluate_evidence_consistency(meta, "pay_N9vKl4M29Lp1", ledger)
    assert report.is_consistent is True
    assert report.consistency_score >= 0.8
    assert len(report.discrepancies) == 0


def test_ledger_reconciliation_amount_mismatch():
    ledger = MockRazorpayLedger()
    meta = EvidenceMetadata(
        document_id="doc_test_02",
        document_type="invoice_details",
        extracted_amount=99999.00,  # Modified amount!
        extracted_txn_id="pay_N9vKl4M29Lp1",
        extracted_order_id="order_N8xKm92Lp01"
    )
    report = evaluate_evidence_consistency(meta, "pay_N9vKl4M29Lp1", ledger)
    assert report.is_consistent is False
    assert any("Amount discrepancy" in d for d in report.discrepancies)
