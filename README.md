<div align="center">

# 🛡️ Sentinel-Kernel
### **Autonomous Site Reliability Engineering (SRE) & Self-Healing Incident Agent**

[![Author](https://img.shields.io/badge/Author-Rayana%20Karthikeyan-6366f1?style=for-the-badge&logo=github)](https://github.com/rayanakarthikeyan)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Sandbox](https://img.shields.io/badge/Sandbox-Process_Isolated-success?style=for-the-badge)](https://github.com/rayanakarthikeyan/Sentinel-Kernel)

<p align="center">
  <b>Sentinel-Kernel</b> is an autonomous SRE platform designed to triage production alerts, perform automated Root Cause Analysis (RCA), safely reproduce anomalies inside an isolated ephemeral sandbox, synthesize candidate patches, and deterministically gate code changes with zero-hallucination test verification.
</p>

</div>

---

## ⚡ The Core Problem It Solves

When distributed systems trigger Sev-0 / Sev-1 alerts, engineering teams lose valuable Mean-Time-To-Resolution (MTTR) reading fragmented logs, deciphering call stacks, and manually writing regression reproductions.

Existing LLM code assistants produce *plausible-looking* code edits, but have no execution grounding:
- ❌ They can't confirm whether the bug actually reproduces before writing a fix.
- ❌ They don't test if the generated patch breaks existing unit or integration tests.
- ❌ They introduce subtle regressions into production codebases.

**Sentinel-Kernel introduces a Deterministic Zero-Hallucination Gate**:
> **A patch is only accepted if the failure is reproduced first in an isolated execution sandbox and all tests pass with an exit code of 0 after the patch is applied.**

---

## 📐 System Architecture

```
                    ┌───────────────────────────────┐
                    │   Telemetry / Webhook Alert   │
                    │   (Sentry, OTel, Prometheus)  │
                    └──────────────┬────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────────┐
                    │    Sentinel Triage & RCA      │
                    │   Hypothesis & Target File    │
                    └──────────────┬────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────────┐
                    │   Ephemeral Sandbox Runner    │
                    │    (Isolated Temp FS / Env)   │
                    │  1. Injects reproduction test │
                    │  2. Verifies bug repro (RC!=0)│
                    └──────────────┬────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────────┐
                    │     Self-Healing Synthesis    │
                    │  Generates Unified Patch Diff │
                    └──────────────┬────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────────┐
                    │  Deterministic Verification   │
                    │  Re-runs sandbox test suite   │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
           [ Tests Pass: Exit 0 ]        [ Tests Fail / Timeout ]
        ┌───────────────────────────┐  ┌─────────────────────────┐
        │ • Verified Pull Request   │  │ • Feed back test errors │
        │ • SRE Post-Mortem Doc     │  │ • Re-attempt or Escalate│
        └───────────────────────────┘  └─────────────────────────┘
```

---

## 🚀 Key Capabilities

- 🔍 **Automated Incident Triage**: Inspects incoming stack traces, log bursts, and telemetry metadata to derive severity scores (`P0`, `P1`, `P2`, `P3`) and target source files.
- 🧪 **Ephemeral Sandbox Isolation**:
  - Operates inside sterile, isolated directories with timeout protection (preventing infinite loops or runaway test runners).
  - Copies minimal workspace context without polluting the host environment or production git branches.
- 🔁 **Closed-Loop Self-Healing**:
  - Automatically synthesizes regression test scripts.
  - Generates unified patches (`.diff`) for clean human-in-the-loop review.
- 📑 **Instant SRE Post-Mortem Generation**: Produces formatted incident post-mortems summarizing timeline, root cause analysis, test reproduction results, and diffs.
- 🌐 **Production REST API**: Built on FastAPI with endpoints for webhooks, incident listing, and simulation triggers.

---

## 🛠️ Tech Stack

- **Core Engine & Schemas**: Python 3.10+, Pydantic v2
- **Sandbox Execution**: Python `subprocess`, temporary filesystem isolation, strict timeout monitors
- **API & Streaming Server**: FastAPI, Uvicorn, Starlette
- **Testing & Verification**: Pytest, Python `unittest`

---

## 📦 Quickstart & Installation

### 1. Clone the repository
```bash
git clone https://github.com/rayanakarthikeyan/Sentinel-Kernel.git
cd Sentinel-Kernel
```

### 2. Install dependencies
```bash
pip install -e .
```

### 3. Run the automated test suite
```bash
python -m unittest tests/test_sentinel.py
```

### 4. Start the Incident Server
```bash
uvicorn sentinel.server.app:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation will be available at `http://localhost:8000/docs`.

### 5. Trigger a Simulation Incident
```bash
curl -X POST "http://localhost:8000/api/simulation/sample-incident"
```

---

## 👤 Author

**Rayana Karthikeyan**
- **GitHub:** [@rayanakarthikeyan](https://github.com/rayanakarthikeyan)
- **LinkedIn:** [linkedin.com/in/rayanakarthikeyan](https://www.linkedin.com/in/rayanakarthikeyan)
- **Portfolio:** [rayanakarthikeyan.vercel.app](https://rayanakarthikeyan.vercel.app/)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
