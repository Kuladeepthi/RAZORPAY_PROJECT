"""
SentinelEvidence — Layer 2 Data Models & Schemas

Pydantic data schemas mirroring Razorpay's public Disputes & Payments API definitions.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TransactionRecord(BaseModel):
    payment_id: str = Field(..., description="Razorpay payment ID e.g. pay_N9vKl4M29Lp1")
    order_id: str = Field(..., description="Razorpay order reference ID e.g. order_N8xKm92Lp01")
    amount: float = Field(..., description="Captured transaction amount in INR")
    currency: str = Field(default="INR")
    status: str = Field(default="captured")
    customer_email: str = Field(..., description="Payer email address")
    customer_contact: Optional[str] = None
    created_at: str = Field(..., description="Payment timestamp in ISO format")
    merchant_name: str = Field(..., description="Registered merchant legal name")


class DisputeObject(BaseModel):
    dispute_id: str = Field(..., description="Razorpay dispute entity ID e.g. disp_98af72bc91")
    payment_id: str = Field(..., description="Associated payment entity ID")
    amount: float = Field(..., description="Disputed chargeback amount")
    currency: str = Field(default="INR")
    reason_code: str = Field(..., description="Razorpay reason code e.g. RZP01")
    phase: str = Field(default="chargeback", description="fraud | retrieval | chargeback | pre_arbitration")
    status: str = Field(default="open", description="open | under_review | won | lost | closed")
    respond_by: int = Field(..., description="Unix timestamp deadline to submit evidence")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Structured evidence payload mapping")


class EvidenceMetadata(BaseModel):
    document_id: str = Field(..., description="Internal document reference ID e.g. doc_8f192b")
    document_type: str = Field(..., description="Classified category e.g. proof_of_delivery, invoice_details")
    extracted_amount: Optional[float] = None
    extracted_txn_id: Optional[str] = None
    extracted_order_id: Optional[str] = None
    extracted_date: Optional[str] = None
    extracted_merchant: Optional[str] = None
    ocr_raw_text: str = ""
    ocr_confidence: float = 1.0


class ConsistencyReport(BaseModel):
    consistency_score: float = Field(..., description="Normalized 0.0 - 1.0 match score")
    is_consistent: bool = Field(..., description="True if entity matching meets threshold")
    matched_payment_id: bool = False
    matched_amount: bool = False
    matched_date: bool = False
    matched_order_id: bool = False
    discrepancies: List[str] = Field(default_factory=list)
    ledger_record: Optional[TransactionRecord] = None
