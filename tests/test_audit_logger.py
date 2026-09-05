"""Tests for Cryptographic Hash Chaining and Audit Logger Integrity."""

import tempfile
from pathlib import Path
from src.agent.audit_logger import AuditLogger, GENESIS_HASH


def test_hash_chain_creation_and_progression():
    with tempfile.TemporaryDirectory() as tmp_dir:
        log_file = Path(tmp_dir) / "test_audit.jsonl"
        logger = AuditLogger(log_file=str(log_file))

        # 1. First Entry (Genesis Block)
        entry1 = logger.log_decision(
            dispute_id="disp_001",
            payment_id="pay_001",
            decision="ACCEPT",
            tamper_score=0.04,
            consistency_score=1.0,
            reasons=["All checks passed"],
            forensic_signals={"ela_score": 0.02}
        )
        assert entry1.block_height == 0
        assert entry1.previous_hash == GENESIS_HASH
        assert len(entry1.provenance_hash) == 24

        # 2. Second Entry (Block 1 chained to Block 0)
        entry2 = logger.log_decision(
            dispute_id="disp_002",
            payment_id="pay_002",
            decision="REJECT",
            tamper_score=0.92,
            consistency_score=0.72,
            reasons=["Tampered amount"],
            forensic_signals={"ela_score": 0.88}
        )
        assert entry2.block_height == 1
        assert entry2.previous_hash == entry1.provenance_hash
        assert entry2.provenance_hash != entry1.provenance_hash

        # 3. Third Entry (Block 2 chained to Block 1)
        entry3 = logger.log_decision(
            dispute_id="disp_003",
            payment_id="pay_003",
            decision="ABSTAIN",
            tamper_score=0.45,
            consistency_score=1.0,
            reasons=["Inconclusive ELA"],
            forensic_signals={"ela_score": 0.45}
        )
        assert entry3.block_height == 2
        assert entry3.previous_hash == entry2.provenance_hash

        # 4. Verify Full Chain Integrity
        report = logger.verify_chain_integrity()
        assert report["is_valid"] is True
        assert report["total_blocks"] == 3
        assert report["chain_status"] == "CRYPTOGRAPHICALLY_VERIFIED"
        assert report["genesis_hash"] == entry1.provenance_hash
        assert report["tip_hash"] == entry3.provenance_hash
        assert report["broken_block_index"] is None


def test_hash_chain_tamper_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        log_file = Path(tmp_dir) / "test_audit_tampered.jsonl"
        logger = AuditLogger(log_file=str(log_file))

        logger.log_decision("disp_001", "pay_001", "ACCEPT", 0.04, 1.0, ["OK"], {})
        logger.log_decision("disp_002", "pay_002", "REJECT", 0.95, 0.5, ["TAMPER"], {})

        # Maliciously mutate block 0 in the JSONL file
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Tamper decision from ACCEPT to FORGED_ACCEPT
        lines[0] = lines[0].replace("ACCEPT", "FORGED_ACCEPT")
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Verification must catch the tampering
        report = logger.verify_chain_integrity()
        assert report["is_valid"] is False
        assert report["chain_status"] in ["HASH_MISMATCH_TAMPER_DETECTED", "BROKEN_CHAIN_LINK"]
