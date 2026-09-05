# 🎬 DisputeLens AI — Official 5-Minute Pitch & Technical Demo Script
### Razorpay AI Buildathon 2026 · Track 2: AI Risk Manager
**Project Brand**: **DisputeLens AI** (*Autonomous Multimodal Chargeback Forensics & Dispute Defense*)  
**Target Duration**: Exactly 5 Minutes (300 Seconds)  
**Target Environment**: Streamlit Dashboard on `http://localhost:8501/`  
**Presenter Tone**: Confident, technical, clear, fintech-native.

---

## 📋 Pre-Recording Setup Checklist (Do This First!)
1. **Browser**: Open Chrome/Edge at `http://localhost:8501/` maximized at 1080p.
2. **Audio**: Test microphone for clear audio with zero background noise.
3. **Recording Software**: Use OBS Studio, Loom, or Windows Game Bar (`Win + G`) to record both screen and voiceover.
4. **Tabs**: Start on **Tab 1: 🔍 Live Forensic Triage**.

---

## ⏱️ Exact Second-by-Second Video Choreography & Script

---

### 🕒 Section 1: The Problem & The Asymmetric Chargeback Threat (0:00 – 0:50)

#### 🎥 On-Screen Actions:
* **[0:00 - 0:25]**: Display the **DisputeLens AI** header banner on `http://localhost:8501/`. Point cursor at the Sidebar showing Razorpay Reason Code `10.4` and the `💰 Financial ROI Engine` card.
* **[0:25 - 0:50]**: Highlight the two distinct threat vectors on screen.

#### 🎙️ Word-for-Word Voiceover:
> *"Hello judges! I am excited to present **DisputeLens AI** — an autonomous multimodal chargeback forensics and dispute defense engine designed specifically for Razorpay and its merchants.
>
> Every month, Indian merchants lose crores in revenue to chargeback disputes under UPI and card networks. But modern payment fraud has evolved into two fundamentally different threats:
>
> **Threat Model A (Ledger Fraud)**: Where fraudsters alter numerical invoice amounts or fake payment IDs.
>
> **Threat Model B (Visual-Only Fraud)**: Where the ledger details are 100% legitimate, but the uploaded delivery slip, recipient signature, or company stamp has been visually spliced or inpainted.
>
> Traditional tabular models fail on visual forgeries, while raw LLMs hallucinate and can't inspect pixel frequency grids. DisputeLens AI solves this with a **Two-Pillar Defense**: fusing settlement ledger reconciliation with computer vision forensics to deliver automated, zero-friction dispute defense."*

---

### 🕒 Section 2: Live Forensic Triage & Interactive Lens (0:50 – 2:05)

#### 🎥 On-Screen Actions:
* **[0:50 - 1:15] Demo Case 1 (Genuine Merchant Invoice)**:
  * Click radio button: **`Genuine Merchant Invoice`**.
  * Point cursor to KPI badges: **Tamper Score: `0.00 (Authentic)`**, **Ledger Match: `100% (Reconciled)`**, and **Gate: `✅ GATE: ACCEPT`**.
  * Mention: *"Zero merchant friction — genuine invoices auto-clear instantly."*
* **[1:15 - 1:40] Demo Case 2 (Forged Amount / Cloned Digit)**:
  * Click radio button: **`Forged Amount (Cloned Digit)`**.
  * Point cursor to KPI badges: **Tamper Score: `0.88`**, **Gate: `🚫 GATE: REJECT (Fraud Alert Blocked)`**.
  * Show the Reason Log: *"Extracted ₹99,999.00 vs Ledger ₹12,499.00 — caught with 100% certainty by Layer 2."*
* **[1:40 - 2:05] Demo Case 3 (Tampered Delivery Slip & Interactive Lens)**:
  * Click radio button: **`Tampered Delivery Slip (AI Inpainted)`**.
  * Show Gate: **`⚠️ GATE: ABSTAIN (Human Ops Review)`**.
  * Click sub-tab **`🔬 Interactive Lens (Blend & ROI)`**.
  * **Drag the slider** from `0%` to `100%` to show the thermal heatmap fading over the document and highlighting the **`[TAMPER ROI: Spliced POD]`** bounding box!
  * Scroll down and show the **3 Human-in-the-Loop Escrow Buttons** (`Force Override & Draft`, `Request Evidence from Merchant`, `Accept Dispute & Refund`).

#### 🎙️ Word-for-Word Voiceover:
> *"Let's see DisputeLens in action on live payment evidence:
>
> First, on a **Genuine Merchant Invoice**, our engine evaluates the document in milliseconds. The tamper score is 0.00, the ledger matches 100%, and the gate immediately outputs **ACCEPT** with zero merchant friction.
>
> Next, consider an amateur fraudster who cloned digits to inflate an invoice from ₹12,499 to ₹99,999. Layer 2 cross-references Razorpay's core banking database, detects the discrepancy, and triggers **REJECT: Fraud Alert Blocked**.
>
> Finally, look at sophisticated **Threat Model B fraud** — an altered BlueDart delivery slip where ledger amounts match, but the physical signature is inpainted. The gate safely defers to **ABSTAIN: Human Ops Review**.
>
> Using our **Interactive Forensic Lens**, risk analysts can drag the blend slider to reveal localized thermal anomalies and bounding box ROI tags, and take instant 1-click human-in-the-loop escrow actions without leaving the console."*

---

### 🕒 Section 3: Live Razorpay Gateway Webhook & Rebuttal PDF (2:05 – 3:10)

#### 🎥 On-Screen Actions:
* **[2:05 - 2:40] Tab 3 (Live Razorpay Gateway Simulator)**:
  * Click **`⚡ Live Razorpay Gateway Simulator`** tab.
  * Show incoming `dispute.created` webhook JSON payload.
  * Click **`🚀 Trigger Live Webhook Autonomous Ingestion`**.
  * Watch the progress spinner complete in `0.84s` and display the outgoing `POST /v1/disputes/{id}/contest` API payload with evidence URLs and cryptographic SHA-256 seal.
* **[2:40 - 3:10] Tab 2 (Dispute Defense & PDF Packet)**:
  * Click **`📝 Dispute Defense & PDF Packet`** tab.
  * Show the auto-drafted legal rebuttal letter referencing Visa Compelling Evidence 3.0 / Mastercard 4837 rules.
  * Type a quick edit into the text box (e.g. adding `"- Case verified by Senior Risk Officer"`).
  * Click **`🛡️ Approve & Export Formal Defense PDF Packet`** and click **`📥 Download Official Defense Packet (PDF)`**.

#### 🎙️ Word-for-Word Voiceover:
> *"Now let's examine real-world payment gateway integration in Tab 3.
>
> When Razorpay receives an incoming **`dispute.created`** webhook event, DisputeLens AI automatically ingests the payload, performs multimodal verification in under 0.9 seconds, and compiles the outgoing **`POST /v1/disputes/{id}/contest`** API call adhering strictly to Razorpay's Dispute Representment schema.
>
> In Tab 2, our Bounded LLM Agent drafts a formal rebuttal letter citing Visa Compelling Evidence 3.0 and Mastercard 4837 rules. Analysts can customize the draft, and DisputeLens compiles a formal, bank-ready PDF packet with cryptographic seals in a single click."*

---

### 🕒 Section 4: AI Risk Copilot & Portfolio Batch Operations (3:10 – 4:10)

#### 🎥 On-Screen Actions:
* **[3:10 - 3:45] Tab 4 (Ask DisputeLens AI Risk Copilot)**:
  * Click **`🤖 Ask DisputeLens AI Risk Copilot`** tab.
  * Click the prompt button: **`⚖️ What Visa CE 3.0 rule applies?`**
  * Show the instant structured legal response detailing Reason Code 10.4 and evidence requirements.
  * Click **`🔬 Why did ELA/Tamper score spike?`** to show the CV signal breakdown.
* **[3:45 - 4:10] Tab 6 (Portfolio Batch Triage & CSV)**:
  * Click **`📦 Portfolio Batch Triage & CSV`** tab.
  * Click **`🚀 Run Concurrent Portfolio Forensic Scan (20 Disputes)`**.
  * Watch the progress bar complete and show portfolio volume (₹522,980.00) and risk distribution metrics.
  * Click **`📥 Download Batch Forensic Triage Report (CSV)`**.

#### 🎙️ Word-for-Word Voiceover:
> *"In Tab 4, we introduce **Ask DisputeLens** — an interactive conversational AI Risk Copilot grounded in card scheme jurisprudence and computer vision theory. Analysts can ask complex regulatory questions, such as how Visa CE 3.0 applies to a digital invoice, or diagnose why an ELA compression variance spiked.
>
> For enterprise risk operations, Tab 6 provides **Portfolio Batch Triage**, scanning 20 merchant chargeback disputes concurrently with real-time risk distribution metrics and instant CSV export."*

---

### 🕒 Section 5: Methodological Rigor, Cost Curves & Closing (4:10 – 5:00)

#### 🎥 On-Screen Actions:
* **[4:10 - 4:40] Tab 5 (Benchmarks & Rupee Cost Curves)**:
  * Click **`📊 Benchmarks & Rupee Cost Curves`** tab.
  * Show the $3\times2$ decision matrix: **100.0% Merchant Auto-Clearance**, **0.0% False Rejections**, **100% Ledger Fraud Interception**.
  * Point cursor to the interactive Plotly **Rupee Loss vs. Rejection Threshold Curve** showing optimal threshold at $T_{\text{reject}} = 0.65$.
* **[4:40 - 5:00] Tab 7 (Decision Audit Trail) & GitHub Repository**:
  * Click **`🛡️ Decision Audit Trail`** to show the SHA-256 provenance ledger.
  * Show the terminal/GitHub repo passing all 13 unit tests.

#### 🎙️ Word-for-Word Voiceover:
> *"Methodological rigor is the cornerstone of DisputeLens AI.
>
> In Tab 5, our empirical benchmark on unseen held-out templates demonstrates **100% seamless auto-clearance** on genuine merchant evidence, **zero false accusations**, and **100% interception** on monetary fraud. Our cost-optimization curve mathematically balances review costs against fraud loss to find the optimal operating threshold.
>
> Every decision is cryptographically anchored in our immutable audit trail.
>
> With 13 passing unit tests, deterministic reproducible evaluation, and end-to-end Razorpay API alignment, **DisputeLens AI** transforms chargeback defense from a costly headache into an automated revenue-protecting moat.
>
> Thank you!"*

---

## 🎯 Pro Tips for a Winning 10/10 Video
1. **Speak with Energy & Confidence**: Don't rush; pause for 1 second when switching tabs to let judges absorb the UI.
2. **Cursor Movement**: Move your mouse deliberately to guide the judges' eyes to the exact metrics you are talking about.
3. **Keep the Script Visible**: Have this script on a second monitor or your phone while recording your main screen.
4. **Time Check**: Practice once with a stopwatch — 5 minutes is plenty of time to hit all 5 sections cleanly!
