# SentinelEvidence — Deep Architecture & Build Spec
### Razorpay AI Buildathon · Track 2: AI Risk Manager
### Grounded in Razorpay's actual public Disputes API

---

## 0. Why this grounding matters

Most entrants will build against an imagined fraud dataset. You're building against **Razorpay's real Disputes object model** — the same `evidence` schema, `reason_code` taxonomy, and `phase` lifecycle their own merchants use today via `POST /v1/disputes/{id}/contest`. This is verifiable from their public docs, so it's not a guess — a Razorpay engineer reading your README will recognize their own API surface immediately. That recognition is worth more than any accuracy number.

**Real Razorpay dispute lifecycle** (from `razorpay.com/docs/api/disputes`):
- `status`: `open → under_review → won / lost / closed`
- `phase`: `fraud | retrieval | chargeback | pre_arbitration`
- `respond_by`: a hard deadline (Unix timestamp) — miss it and you auto-lose
- `evidence` object fields: `shipping_proof`, `billing_proof`, `cancellation_proof`, `customer_communication`, `proof_of_service`, `explanation_letter`, `refund_confirmation`, `access_activity_log`, `refund_cancellation_policy`, `term_and_conditions`, `others[]` (each with a `type` and `document_ids[]`)
- Evidence documents are uploaded via the separate **Documents API** and referenced by `doc_id`

**Real Razorpay reason codes** (from `razorpay.com/docs/payments/disputes/submit-evidence`) — this is the exact taxonomy your system should reason over:

| Reason Code | Meaning | Required Evidence Types |
|---|---|---|
| RZP00 | Not available / doesn't fit other categories | delivery proof, invoice details, email communication, refund details |
| RZP01 | Goods/Services not provided | proof of delivery, customer interaction, T&C |
| RZP04 | Refund not processed | refund generation proof, bank statement, refund confirmation comms |
| RZP05 | Account debited, no confirmation | invoice (if captured), internal logs (if failed), customer interaction |
| RZP06 | Business not responding | delivery proof within committed timeline, invoicing details, email comms |

This table is your **decision policy lookup** — the agent doesn't freelance which evidence to request or draft around; it looks up the reason code and knows exactly what evidence classes are relevant, exactly like a real dispute analyst would.

---

## 1. Full system architecture

```
                                   RAZORPAY DISPUTE OBJECT
                          {reason_code, phase, respond_by, amount}
                                          │
                                          ▼
                     ┌───────────────────────────────────────┐
                     │  0. Reason-Code Policy Engine           │
                     │  (lookup table → required evidence types)│
                     └───────────────────────────────────────┘
                                          │
                     evidence documents uploaded (images/PDFs)
                                          │
          ┌───────────────────────────────┼───────────────────────────────┐
          ▼                                ▼                                ▼
┌──────────────────────┐    ┌──────────────────────────┐    ┌─────────────────────────┐
│ 1. Forensic Layer      │    │ 2. Content-Consistency    │    │ 3. Completeness Checker  │
│ (OpenCV + DL)          │    │ Layer (OCR + matching)     │    │ (does the doc set match  │
│ ELA / copy-move /       │    │ vs mock order/txn record   │    │  what RZP0x requires?)   │
│ double-compression /    │    │                            │    │                          │
│ CNN tamper localizer    │    │                            │    │                          │
└──────────────────────┘    └──────────────────────────┘    └─────────────────────────┘
          │                                │                                │
          └────────────────┬───────────────┴────────────────┬───────────────┘
                            ▼                                ▼
                 ┌─────────────────────────────────────────────┐
                 │  4. Cost-Calibrated Fusion & Decision Gate     │
                 │  ACCEPT → draft   ABSTAIN → human   REJECT → flag│
                 └─────────────────────────────────────────────┘
                            │
                 ┌─────────────────────────────────────────────┐
                 │  5. Agentic Responder (LangChain, bounded)     │
                 │  populates evidence{} object fields +          │
                 │  drafts explanation_letter, cites doc_ids only │
                 └─────────────────────────────────────────────┘
                            │
                 ┌─────────────────────────────────────────────┐
                 │  6. Human Review Dashboard + Audit Log         │
                 │  (only human click actually "submits")         │
                 └─────────────────────────────────────────────┘
```

---

## 2. Layer-by-layer deep dive

### Layer 0 — Reason-Code Policy Engine
A simple, explicit lookup table (not a model) mapping `reason_code → [required_evidence_types]`, built directly from Razorpay's published table above. This does two jobs:
1. Tells the completeness checker (Layer 3) what's *missing* before anything else runs
2. Tells the agent (Layer 5) which `evidence{}` fields it's allowed to populate for this specific dispute

Keep this a plain, auditable dictionary/JSON — resist the urge to "ML-ify" this part. Judges will notice you knew *not* to use a model where a lookup table is the right tool. That restraint is itself a signal of AI Judgment.

### Layer 1 — Forensic Authenticity (your CV/cybersecurity core)
Four fused signals, ensembled the same way you late-fused SENTINEL's static+dynamic branches:

1. **Error Level Analysis (ELA)** — recompress at fixed JPEG quality (~90), diff against original. Tampered regions show elevated recompression error because their local compression history differs from the rest of the image.
2. **Copy-move detection** — ORB keypoints + Lowe's ratio test + RANSAC-filtered affine clustering to find duplicated regions within the same document (classic move: duplicating a "0" or a signature).
3. **Double-JPEG / DCT quantization analysis** — periodicity in the DCT coefficient histogram reveals a second compression pass, a strong signal of post-hoc editing.
4. **Learned localizer** — EfficientNet-B0 (or a small ResNet) fine-tuned on your synthetic tamper data + CASIA v2.0/DocTamper subset, outputting a per-region tamper-probability heatmap. This is what generalizes to tamper types your classical rules miss.

Fuse all four via a small **gradient-boosted meta-model** (LightGBM — you already know this tool intimately) over the four signal scores, calibrated with isotonic regression or Platt scaling so the output is a genuinely interpretable probability, not just a ranking score.

### Layer 2 — Content-Consistency (OCR + NLP)
1. OCR with PaddleOCR (handles receipts/screenshots better than Tesseract for mixed fonts and low-res crops).
2. Field extraction: prefer a **layout-aware extractor** over raw regex-on-OCR-text — a small fine-tuned LayoutLM-style or Donut-style document model reads amount/date/order-ID *with spatial context*, which is far more robust to receipts that don't follow a fixed template. If time is tight, a well-built OCR+regex+fuzzy-match baseline is a legitimate fallback — just say explicitly in your README which one you used and why, that honesty is itself a positive signal.
3. Cross-check extracted fields against your **mock order/transaction database** — exact match on transaction ID, tolerance-band match on amount (±small rounding), date-window match.
4. Output `consistency_score`: independent of whether the image was visually altered. A perfectly "authentic" (unedited) screenshot describing a transaction that never happened is a distinct fraud pattern from a tampered image — your system should be able to say *which* kind of problem it found, not just "fraud/not fraud."

### Layer 3 — Completeness Checker
Given the dispute's `reason_code`, check whether the uploaded evidence documents actually cover the required types from the policy table (e.g. RZP01 needs proof-of-delivery + customer-interaction + T&C). Flag missing categories *before* wasting a drafting cycle on an incomplete case. This is a cheap, high-value component that most entrants won't think to build — it's the difference between "we detect fraud" and "we understand how Razorpay's dispute process actually works."

### Layer 4 — Cost-Calibrated Fusion & Decision Gate
Combine `tamper_score`, `consistency_score`, and `completeness` into one gate:

```python
def decide(tamper_score, consistency_score, completeness_ok):
    if not completeness_ok:
        return "ABSTAIN", "missing required evidence type for this reason_code"
    if tamper_score > 0.7 or consistency_score < 0.3:
        return "REJECT", f"tamper={tamper_score:.2f} consistency={consistency_score:.2f}"
    if tamper_score < 0.3 and consistency_score > 0.7:
        return "ACCEPT", "passes forensic and consistency checks"
    return "ABSTAIN", f"ambiguous band: tamper={tamper_score:.2f} consistency={consistency_score:.2f}"
```

Pick the 0.3/0.7 thresholds **from your cost curve, not arbitrarily** — plot expected rupee cost (false REJECT delays a legitimate merchant's payout; false ACCEPT risks losing a real dispute with fabricated evidence) against threshold and choose the minimum-cost point. Report this curve in your submission; it's exactly the "honest metrics including false-positive cost" bar Razorpay named explicitly.

### Layer 5 — Agentic Responder
For ACCEPT-gated cases only, a LangChain agent (same bounded-tool pattern as your AgentShield project):
- Reads the dispute's `reason_code` + evidence documents + consistency report
- Populates the relevant Razorpay `evidence{}` object fields (`shipping_proof`, `proof_of_service`, etc. as `doc_id` references — never raw content)
- Drafts `explanation_letter` text citing specific, verified evidence — never inventing facts not present in the extracted data
- Writes a structured log entry to the audit trail

Hard constraints (state these explicitly in your README, they map directly to the "strictly defense-only, offense-capable = disqualified" rule):
- The agent cannot call any endpoint that actually submits to a bank/network
- The agent cannot alter tamper/consistency scores
- Every draft requires a human "Approve & Log" click in the dashboard before anything is considered final

### Layer 6 — Dashboard + Audit Trail
Streamlit app with tabs: **Live Triage** (upload evidence, see the ELA/copy-move overlay, consistency report, and gate decision), **Drafted Response** (agent output + approve button, ACCEPT cases only), **Metrics** (precision/recall curves, cost curve, abstention rate over your test set), **Audit Log** (every decision ever made, timestamped, with the reason string — this is your Failure Recovery evidence).

---

## 3. Data plan (this determines your credibility more than model choice)

### 3a. Public datasets for pretraining forensic signals
- SROIE-derived receipt forgery set (988 receipts, 163 with annotated realistic tamper)
- CASIA v2.0 (~7,491 authentic / ~5,123 tampered, splicing + copy-move)
- DocTamper subset if accessible (pixel-level masks, receipts/invoices/contracts)

### 3b. Your own synthetic generator — mirrors real Razorpay evidence types
Build clean template documents that mimic the actual Razorpay evidence categories: a UPI payment-success screenshot, a courier tracking/delivery-confirmation page, a GST invoice, a refund-confirmation email screenshot, a T&C page. Programmatically tamper a subset of each type:
- copy-move a field (duplicate an amount/date)
- splice a region from a different document
- re-render a digit/text field in a mismatched font (simulates screenshot editing)
- blur-and-reconstruct a region (approximates inpainting-tool artifacts)

This gives you labeled ground truth **specific to the Razorpay evidence taxonomy**, not generic natural images — a much stronger claim in your pitch than "we used a Kaggle dataset."

### 3c. Mock transaction/order database
Build a CSV of ~200–500 synthetic transactions with fields matching what Razorpay's real Payment/Order entities expose (`payment_id`, `amount`, `created_at`, `order_id`, `customer_email`) — this is what Layer 2 cross-checks evidence claims against.

### 3d. Split discipline
Split by **source template document**, never by random crop — the same base receipt template must never appear in both train and test, or your precision/recall numbers are inflated and a technical panelist will catch it in ten seconds.

---

## 4. Evaluation — what to actually report

- Precision / Recall / F1 / ROC-AUC on held-out, template-split test set, for tamper detection specifically
- Same metrics for the consistency layer, evaluated separately (don't conflate the two failure modes)
- **Cost curve**: rupee cost of false-REJECT vs false-ACCEPT across thresholds, with your chosen operating point marked and justified
- **Abstention rate** and what fraction of abstained cases a human reviewer agrees needed review (even a small manual audit of 20 abstained cases with your own judgment as ground truth is a credible mini-study)
- **Robustness gap**: performance on your AI-inpainting-style synthetic subset vs classical-tamper subset, reported honestly even though it's the weaker number — this is the single most convincing "I understand the frontier of this problem" signal you can give a technical panel

---

## 5. What makes this genuinely hard to copy
1. It requires reading and correctly modeling Razorpay's *actual* API schema — not generic fraud tropes
2. It requires forensic imaging techniques most ML-only candidates have never touched
3. It requires the discipline to keep the agent bounded and auditable rather than "just let the LLM decide" — showing restraint under an AI-hype framing is a mature signal
4. It requires being honest about a weak spot (AI-forged robustness) instead of hiding it

## 6. Judging-criteria mapping
- **Problem Taste** → grounded in Razorpay's own named example direction *and* their real reason-code taxonomy
- **Build Quality** → layered, testable repo; policy engine kept explicit instead of over-modeled
- **AI Judgment** → four different techniques (classical forensics, learned CV, OCR/NLP, LLM agent) each applied where it's the right tool, with an explicit case (Layer 0) where you *chose not* to use ML
- **Failure Recovery** → the ABSTAIN band with logged reasons, the completeness checker catching incomplete evidence before wasted work, and the honestly reported AI-forgery robustness gap
