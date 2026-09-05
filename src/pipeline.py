"""
SentinelEvidence — Master Pipeline Orchestrator

Connects all 6 architectural layers:
- Layer 0: Reason-Code Policy Engine
- Layer 1: Forensic Image Analysis (ELA, Copy-Move, Double-JPEG, Heatmap)
- Layer 2: OCR Entity Extraction & Ledger Reconciliation
- Layer 3: Reason-Code Evidence Completeness Check
- Layer 4: Cost-Calibrated Decision Gate
- Layer 5: Bounded Agentic Drafter & Audit Logging
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
from PIL import Image

from .policy.reason_code_policy import check_completeness
from .forensics.fusion import run_forensic_pipeline
from .consistency.models import DisputeObject, EvidenceMetadata
from .consistency.ocr_engine import extract_document_entities
from .consistency.ledger_matcher import MockRazorpayLedger, evaluate_evidence_consistency
from .decision.cost_gate import evaluate_decision_gate, GateDecision, DecisionOutcome
from .agent.responder_agent import draft_dispute_response, DisputeResponsePacket
from .agent.audit_logger import AuditLogger


class SentinelPipeline:
    def __init__(self, ledger: Optional[MockRazorpayLedger] = None):
        self.ledger = ledger or MockRazorpayLedger()
        self.audit_logger = AuditLogger()

    def process_dispute(
        self,
        dispute: DisputeObject,
        evidence_image: Union[str, np.ndarray, Image.Image],
        document_type: str = "proof_of_delivery",
        doc_id: str = "doc_upload_01",
        known_entities: Optional[Dict[str, Any]] = None,
        all_uploaded_document_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end verification and triage on a dispute case.
        """
        # --- Layer 1: Forensic Analysis ---
        forensic_res = run_forensic_pipeline(evidence_image)
        tamper_score = forensic_res["tamper_score"]

        # --- Layer 2: OCR & Consistency Matching ---
        evidence_meta = extract_document_entities(
            image_input=evidence_image,
            doc_id=doc_id,
            document_type=document_type,
            known_metadata=known_entities
        )
        consistency_report = evaluate_evidence_consistency(
            evidence=evidence_meta,
            payment_id=dispute.payment_id,
            ledger=self.ledger
        )

        # --- Layer 3: Completeness Checker ---
        uploaded_types = set(all_uploaded_document_types or [document_type])
        completeness_res = check_completeness(dispute.reason_code, uploaded_types)

        # --- Layer 4: Cost-Calibrated Decision Gate ---
        gate_decision: GateDecision = evaluate_decision_gate(
            tamper_score=tamper_score,
            consistency_score=consistency_report.consistency_score,
            completeness_result=completeness_res,
            dispute_amount=dispute.amount
        )

        # --- Layer 5: Agentic Drafter (for ACCEPT cases) ---
        response_packet: Optional[DisputeResponsePacket] = None
        if gate_decision.decision == DecisionOutcome.ACCEPT:
            response_packet = draft_dispute_response(
                dispute=dispute,
                evidence_list=[evidence_meta],
                consistency=consistency_report,
                forensic_hash=f"auth_sha256_{doc_id[:6]}"
            )

        # --- Audit Logging ---
        audit_entry = self.audit_logger.log_decision(
            dispute_id=dispute.dispute_id,
            payment_id=dispute.payment_id,
            decision=gate_decision.decision.value,
            tamper_score=tamper_score,
            consistency_score=consistency_report.consistency_score,
            reasons=gate_decision.reasons,
            forensic_signals=forensic_res["signals"],
            approval_status="AUTO_DRAFTED" if response_packet else "TRIAGED"
        )

        return {
            "dispute_id": dispute.dispute_id,
            "payment_id": dispute.payment_id,
            "reason_code": dispute.reason_code,
            "gate_decision": gate_decision.model_dump(),
            "forensics": forensic_res,
            "consistency": consistency_report.model_dump(),
            "completeness": completeness_res,
            "response_packet": response_packet.model_dump() if response_packet else None,
            "audit_entry": audit_entry.model_dump(),
        }
