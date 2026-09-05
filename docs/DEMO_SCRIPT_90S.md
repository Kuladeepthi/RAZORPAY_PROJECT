# 🎬 SentinelEvidence — 90-Second Demo Video Script
### Razorpay AI Buildathon · Track 2: AI Risk Manager
**Format**: High-impact, fast-paced video walkthrough (Loom / Screen Recording + Voiceover)

---

### **[00:00 - 00:15] The Hook & Razorpay Grounding**
* **Visual**: Show Razorpay Disputes API docs (`POST /v1/disputes/{id}/contest`) & dispute reason codes RZP00–RZP06.
* **Voiceover**:  
  > *"Every month, Indian merchants lose crores to chargeback fraud under UPI and Card networks. Today, merchants either manually review thousands of uploaded documents or lose disputes by default. Meet **SentinelEvidence** — Razorpay’s first two-pillar AI evidence verification engine built directly on Razorpay's dispute reason codes RZP00 through RZP06."*

---

### **[00:15 - 00:40] The Two-Pillar Architecture in Action**
* **Visual**: In Streamlit Dashboard (Tab 1), show a tampered dispute. Click **"Execute Multi-Layer Forensic Triage"**.
* **Voiceover**:  
  > *"SentinelEvidence replaces brittle single-point heuristics with a **Two-Pillar Defense**:  
  > **Pillar 1 (Ledger Reconciliation)** extracts the transaction ID and amount, cross-checking them against Razorpay's immutable settlement database to block monetary fraud with 100% certainty.  
  > **Pillar 2 (Visual Forensics)** runs Error Level Analysis, DCT quantization analysis, and Regional Copy-Move feature clustering to catch cloned company stamps and spliced signatures on uploaded documents."*

---

### **[00:40 - 01:05] Methodological Integrity & The 3×2 Triage Gate**
* **Visual**: Switch to Tab 3 (Multi-Threat Matrix & Rupee Cost Curve).
* **Voiceover**:  
  > *"Unlike naive binary classifiers, our **Cost-Calibrated Decision Gate** explicitly evaluates expected financial loss:  
  > Genuine merchant evidence gets **100% seamless auto-clearance with zero false friction**.  
  > Threat Model A ledger fraud is **100% intercepted** by Layer 2 cross-checks.  
  > For visual-only fraud on lossless PNG screenshots — a genuinely hard open problem in document forensics — our current CV layer has a known frontier (6.2% direct CV block, 93.8% silent leakage on non-duplicate PNG splices), which is why we built Layer 2 ledger reconciliation as an independent second pillar, and why this defines our stated next milestone rather than a claimed solved problem."*

---

### **[01:05 - 01:25] Bounded LLM Drafter & Cryptographic PDF Export**
* **Visual**: Switch to Tab 2 (Auto-Generated Dispute Letter & PDF Export).
* **Voiceover**:  
  > *"When evidence passes, our Bounded LLM Agent drafts a formal, legally grounded rebuttal letter adhering strictly to Razorpay's evidence schema, embeds a SHA-256 cryptographic attestation hash, and generates an official bank-ready PDF packet in one click."*

---

### **[01:25 - 01:30] Conclusion & Call to Action**
* **Visual**: Show GitHub repository badge and terminal test suite passing 13/13.
* **Voiceover**:  
  > *"Built with strict template-split discipline, format-aware forensics, and verifiable integrity. SentinelEvidence turns chargeback defense into an automated revenue-protecting moat for Razorpay merchants."*
