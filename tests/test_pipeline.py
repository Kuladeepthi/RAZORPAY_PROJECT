"""End-to-end integration tests for SentinelPipeline and PDF export."""

from pathlib import Path
import numpy as np
from src.consistency.models import DisputeObject
from src.pipeline import SentinelPipeline
from src.agent.pdf_exporter import export_dispute_pdf
from src.agent.responder_agent import draft_dispute_response


def test_full_pipeline_run():
    pipeline = SentinelPipeline()
    dispute = DisputeObject(
        dispute_id="disp_test_9012",
        payment_id="pay_N9vKl4M29Lp1",
        amount=4850.00,
        reason_code="RZP01",
        respond_by=1787040000
    )

    test_img = np.full((300, 300, 3), 245, dtype=np.uint8)
    known = {
        "extracted_amount": 4850.00,
        "extracted_txn_id": "pay_N9vKl4M29Lp1",
        "extracted_order_id": "order_N8xKm92Lp01"
    }

    result = pipeline.process_dispute(
        dispute=dispute,
        evidence_image=test_img,
        document_type="proof_of_delivery",
        known_entities=known
    )

    assert "gate_decision" in result
    assert "forensics" in result
    assert "consistency" in result
    assert "audit_entry" in result


def test_pdf_packet_generation(tmp_path):
    dispute = DisputeObject(
        dispute_id="disp_test_pdf_01",
        payment_id="pay_N9vKl4M29Lp1",
        amount=4850.00,
        reason_code="RZP01",
        respond_by=1787040000
    )
    pipeline = SentinelPipeline()
    test_img = np.full((300, 300, 3), 245, dtype=np.uint8)
    known = {"extracted_amount": 4850.00, "extracted_txn_id": "pay_N9vKl4M29Lp1", "extracted_order_id": "order_N8xKm92Lp01"}

    res = pipeline.process_dispute(dispute, test_img, "proof_of_delivery", known_entities=known)
    
    # Generate draft
    from src.consistency.models import EvidenceMetadata, ConsistencyReport
    meta = EvidenceMetadata(document_id="doc_pdf_01", document_type="proof_of_delivery", extracted_amount=4850.0)
    consistency = ConsistencyReport(consistency_score=0.95, is_consistent=True, matched_payment_id=True, matched_amount=True)
    packet = draft_dispute_response(dispute, [meta], consistency)

    pdf_out = str(tmp_path / "test_defense_packet.pdf")
    generated_path = export_dispute_pdf(packet, dispute, consistency, pdf_out)
    assert Path(generated_path).exists()
    assert Path(generated_path).stat().st_size > 1000
