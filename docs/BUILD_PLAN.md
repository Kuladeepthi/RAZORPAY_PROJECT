# SentinelEvidence — End-to-End Build Plan
### Razorpay AI Buildathon · Track 2: AI Risk Manager

**One-line pitch:** A forensic authenticity + content-consistency + agentic auto-responder pipeline that verifies chargeback evidence before drafting a dispute response — catching tampered proof (including AI-inpainted forgeries) that today's manual review misses.

---

## 1. Problem framing (why this, precisely)

Razorpay's brief for this track names "Chargeback evidence responder" as an example direction and sets the bar at: *measured precision/recall on a held-out set, honest false-positive cost, strictly defense-only.* Most entrants will build a transaction-level fraud classifier on tabular data. This build instead targets the **evidence layer** of the dispute process — an angle almost nobody else will take, because it requires forensic imaging + OCR/NLP + agentic design together, not just one model.

The threat model in one sentence: *a merchant (or a fraudulent claimant) submits a screenshot/receipt/invoice as chargeback evidence, and either the image has been digitally altered, or its claimed content doesn't match the real transaction record.*

---

## 2. System architecture

```
                ┌─────────────────────────┐
   Evidence     │  1. Forensic Authenticity │
   image/PDF ──▶│     Layer (CV + DL)       │──▶ tamper_score (0-1) + heatmap
                └─────────────────────────┘
                           │
                ┌─────────────────────────┐
                │  2. Content-Consistency   │
                │   Layer (OCR + matching)  │──▶ consistency_score (0-1)
                └─────────────────────────┘
                           │
                ┌─────────────────────────┐
                │  3. Decision Gate         │
                │  (cost-calibrated fusion) │──▶ ACCEPT / ABSTAIN→human / REJECT
                └─────────────────────────┘
                           │
                ┌─────────────────────────┐
                │  4. Agentic Responder     │
                │  (LangChain, bounded)     │──▶ draft dispute packet (ACCEPT only)
                └─────────────────────────┘
                           │
                ┌─────────────────────────┐
                │  5. Audit Trail + Dashboard│  (Streamlit, every decision logged)
                └─────────────────────────┘
```

Nothing auto-submits to a real chargeback system. Every ACCEPT still requires a human "approve & send" click in the dashboard — this is what makes it strictly defense-only per the brief's disqualification clause.

---

## 3. Repository structure

```
sentinel-evidence/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                    # downloaded public datasets (gitignored, README on how to fetch)
│   ├── synthetic/               # your generated tampered/authentic pairs + masks
│   └── splits/                  # train/val/test CSVs (source- or time-based split)
├── src/
│   ├── data_gen/
│   │   └── synthetic_tamper_generator.py
│   ├── forensics/
│   │   ├── ela.py
│   │   ├── copy_move.py
│   │   ├── double_compression.py
│   │   ├── cnn_localizer.py
│   │   └── ensemble.py
│   ├── consistency/
│   │   ├── ocr_extract.py
│   │   └── field_matcher.py
│   ├── agent/
│   │   ├── responder_agent.py
│   │   └── audit_log.py
│   ├── pipeline.py               # ties layers 1-4 together
│   └── evaluate.py               # precision/recall/cost curve, abstention analysis
├── dashboard/
│   └── app.py                    # Streamlit
├── notebooks/
│   └── eda_and_results.ipynb
└── tests/
    └── test_forensics.py
```

---

## 4. Phase 1 — Data (the part most people get lazy about)

### 4a. Real public datasets to ground your work
- **SROIE-derived receipt forgery dataset** — 988 scanned receipts, 163 with realistic fraudulent modifications, annotated. Best small, realistic base for receipts specifically.
- **CASIA v2.0** — ~7,491 authentic / ~5,123 tampered general images (splicing, copy-move). Use to pretrain/validate your general forensic detectors before specializing.
- **DocTamper** — large document-tampering benchmark (copy-move, splicing, print-based edits) with pixel-level masks, if you can access a subset — great for the CNN localizer.

Cite these by name in your README even if you only use a subset — it shows you did real literature grounding, not vibes.

### 4b. Your own synthetic generator (the differentiator)
Public datasets won't look like Razorpay-style evidence (UPI screenshots, courier PODs, GST invoices). Build `synthetic_tamper_generator.py` (scaffold provided) to produce **your own labeled pairs** from clean template documents you create:
- **Copy-move**: duplicate a region (e.g. an amount field) elsewhere in the same doc
- **Splicing**: paste a region from a different document/font
- **Numeric/text tampering**: overwrite a field digit with a re-rendered font (simulates a screenshot-editor edit)
- **Inpainting-style tamper**: blur + reconstruct a region (approximates what an AI inpainting tool would leave as an artifact, without needing paid API access)

This gives you full control of ground truth for honest precision/recall — and it's a strong talking point in your pitch ("we didn't just borrow a dataset, we modeled Razorpay's actual evidence types").

### 4c. Data split discipline
Split by **source document**, never by random pixel-crop, so the same base receipt never appears in both train and test. Mention this explicitly in your README — it's a real signal of ML maturity that most entrants will get wrong.

---

## 5. Phase 2 — Forensic authenticity layer

Three classical signals + one learned signal, fused:

1. **Error Level Analysis (ELA)** — recompress the image at a known JPEG quality and diff against the original; edited regions show elevated error due to inconsistent compression history.
2. **Copy-move detection** — ORB/SIFT keypoint matching within the same image + RANSAC-filtered geometric clustering to find duplicated regions.
3. **Double JPEG compression / quantization artifacts** — detect periodic DCT histogram patterns that indicate the image was compressed twice (a strong tamper signal).
4. **Learned localizer** — a small EfficientNet/ResNet fine-tuned on your synthetic + CASIA/DocTamper data to output a tamper-probability heatmap, catching things the classical signals miss (including some AI-inpainted edits).

Fuse the four into a single calibrated `tamper_score` (logistic fusion or a small gradient-boosted meta-model over the four signal outputs — you already know how to do this from SENTINEL's late-fusion meta-learner).

`src/forensics/` scaffold with working ELA + copy-move code is provided in `forensic_core.py` (see companion file).

---

## 6. Phase 3 — Content-consistency layer

1. OCR the evidence document (Tesseract or PaddleOCR — PaddleOCR handles receipts/invoices better).
2. Extract structured fields: amount, date, order/txn ID, merchant name.
3. Match against a **mock transaction database** (a CSV you construct simulating Razorpay's order records) — exact match on txn ID, fuzzy/tolerance match on amount and date.
4. Output a `consistency_score`: how well the evidence's claimed content matches the real record, independent of whether the image itself was visually tampered. This catches cases where the image is technically unedited but describes a transaction that never happened.

---

## 7. Phase 4 — Agentic auto-responder

Use LangChain (same pattern as your AgentShield project) with a **strict, bounded tool set** — the agent can only:
- read the evidence + consistency report
- draft a response using a fixed template with citations to specific evidence fields
- log to the audit trail

It cannot: submit anything externally, modify the tamper/consistency scores, or bypass the decision gate. Explicitly state this constraint in your README — it's your answer to the "strictly defense-only" requirement.

Decision gate logic:
```
if tamper_score < 0.3 and consistency_score > 0.7:
    → ACCEPT: agent drafts response, human approves
elif tamper_score > 0.7 or consistency_score < 0.3:
    → REJECT: flagged for fraud review, no draft generated
else:
    → ABSTAIN: routed to human reviewer with reason ("forensic signal inconclusive: copy-move confidence 0.52")
```
That middle band and its explicit reason string **is** your Failure Recovery story — real, not fabricated.

---

## 8. Phase 5 — Evaluation (this is what the panel will actually scrutinize)

Report all of these, not just accuracy:
- Precision / Recall / F1 / ROC-AUC on the held-out, source-split test set
- **Cost-weighted analysis**: assign a rupee cost to a false REJECT (legitimate merchant evidence wrongly blocked → delayed payout) vs a false ACCEPT (fraudulent evidence wrongly passed → chargeback loss). Plot cost vs threshold and justify your chosen operating point.
- **Abstention rate**: what % of cases fall in the middle band, and does it drop as you improve the model
- **Robustness test**: run your detector against your AI-inpainted synthetic subset separately from classical-tamper subset, and report the (likely lower) performance honestly — a documented weakness is more credible than a suspiciously perfect number, and shows you understand the AIForge-Doc-style frontier problem.

---

## 9. Phase 6 — Dashboard

Streamlit app (you've built this pattern twice already):
- Upload/select an evidence document
- Show ELA heatmap + copy-move overlay + consistency report side by side
- Show the gate decision and, for ABSTAIN/REJECT, the specific reason
- For ACCEPT, show the agent-drafted response with an "Approve & Log" button (never auto-sends)
- A metrics tab showing the precision/recall/cost curves from Phase 5

---

## 10. Packaging for submission

**README.md** should open with: problem statement → architecture diagram → how to run → metrics table → known limitations (this ordering signals engineering maturity).

**5-min pitch video structure:**
- 0:00–0:45 — the problem, framed in money terms ("chargeback evidence is trusted at face value today")
- 0:45–2:00 — live demo: feed a tampered evidence doc, show the heatmap + rejection
- 2:00–3:00 — live demo: feed a legit doc, show the agent draft + human-approve gate
- 3:00–4:00 — metrics: precision/recall, cost curve, the honest AI-forgery robustness gap
- 4:00–5:00 — architecture recap + what you'd build next (e.g. abuse-ring linking across merchants)

**Form answers:**
- *Project Name*: "SentinelEvidence — Forensic Verification for Chargeback Evidence"
- *Objectives*: "Chargeback evidence is currently trusted at face value or reviewed manually at scale. SentinelEvidence forensically verifies evidence authenticity (including AI-inpainted tampering) and cross-checks its claimed content against the real transaction record before any auto-response is drafted — with a human-in-the-loop gate and full audit trail, so no financial action is ever taken autonomously."
- *Build Challenges*: write this only after you've actually hit real ones — likely candidates: getting a source-based split right without leaking near-duplicate receipts, calibrating the fusion threshold against a cost function instead of accuracy, and PaddleOCR struggling on low-quality screenshots (mention how you handled the low-confidence-OCR case — probably by routing to ABSTAIN too).

---

## 11. Suggested build sequence (not a rigid timeline — sequence matters more than dates)

1. Synthetic data generator + a first small labeled set (fastest thing that unblocks everything else)
2. ELA + copy-move (classical, no training needed — gives you a working pipeline end-to-end fast)
3. CNN localizer trained on synthetic + CASIA/DocTamper subset
4. Consistency layer (OCR + mock transaction DB)
5. Fusion + decision gate + evaluation harness (this is where your precision/recall/cost numbers come from — don't rush this)
6. Agent layer + dashboard (most "impressive" visually, but least differentiating technically — build it last so layers 1-5 are solid first)
7. README + pitch video last, once real numbers exist to report

Use Antigravity to parallelize 2/3 (forensics) against 4 (consistency layer) since they don't depend on each other — that's the natural parallel split.

---

## 12. Stretch goals if time allows
- Extend consistency-matching into a lightweight **abuse-ring signal**: cluster evidence submissions by shared visual/textual fingerprints across "different" merchants to catch coordinated fraud rings (ties into the track's "Abuse-ring sentinel" direction as a bonus, without changing your core pitch).
- Add a zero-shot GPT-4o/Claude-vision judge as a second opinion in the ensemble and report where it agrees/disagrees with your trained detector — interesting ablation, shows LLM judgment awareness.

## 13. Mapping back to Razorpay's four judging criteria
- **Problem Taste** → evidence-layer fraud is real, underserved, and named in their own brief
- **Build Quality** → clean layered repo, source-split evaluation, tests
- **AI Judgment** → classical CV + learned CNN + OCR/NLP + LLM agent, each used where it's actually the right tool — not one model doing everything
- **Failure Recovery** → the explicit ABSTAIN band with logged reasons, and the honest AI-forgery robustness gap
