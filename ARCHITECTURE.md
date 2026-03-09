# Math Mentor – Architecture

## High-level flow

```mermaid
flowchart TB
    subgraph Input["Multimodal input"]
        T[Text]
        I[Image]
        A[Audio]
    end

    subgraph Extract["Extraction"]
        OCR[OCR: Vision / EasyOCR + LLM fix]
        ASR[ASR: Whisper]
        T --> Raw[Raw text]
        I --> OCR --> Raw
        A --> ASR --> Raw
    end

    subgraph HITL_check["HITL gate"]
        Conf{Low confidence?}
        Raw --> Conf
        Conf -->|Yes| Human[Human review / edit]
        Conf -->|No| Parse
        Human --> Parse
    end

    subgraph Agents["Agent pipeline"]
        Parse[Parser: clean, structure, topic]
        Route[Intent Router: strategy]
        RAG[(RAG: Chroma + embeddings)]
        Parse --> Route
        Route --> Solver[Solver: RAG + LLM + optional CALC]
        RAG --> Solver
        Solver --> Verify[Verifier: correctness, confidence]
        Verify --> Explainer[Explainer: step-by-step tutor]
    end

    subgraph HITL_verify["HITL (verifier)"]
        VConf{Low confidence / hitl_required?}
        Verify --> VConf
        VConf -->|Yes| Human2[Human: approve / correct]
        VConf -->|No| Explainer
        Human2 --> Explainer
    end

    subgraph Output["Output & memory"]
        Explainer --> Answer[Answer + explanation]
        Answer --> Store[Memory: store session]
        Store --> Similar[Retrieve similar past problems]
        Similar -.-> Solver
    end

    style Input fill:#e1f5fe
    style Agents fill:#e8f5e9
    style Output fill:#fff3e0
```

## Component summary

| Component | Role |
|-----------|------|
| **OCR** | Image → text (Groq Vision first, EasyOCR + LLM fix fallback). |
| **ASR** | Audio (WAV) → transcript via Whisper. |
| **Parser** | Raw text → structured problem (topic, variables, constraints, needs_clarification). |
| **Intent Router** | Classifies intent (algebra/probability/calculus/linear_algebra), suggests strategy. |
| **RAG** | Chroma + Groq/sentence-transformers embeddings over `knowledge_base/`. Top-k retrieval. |
| **Solver** | Uses RAG context + LLM; optional `CALC: <expr>` for numeric evaluation. |
| **Verifier** | Checks correctness, units, domain; sets confidence and hitl_required. |
| **Explainer** | Turns solution into student-friendly step-by-step explanation. |
| **HITL** | Triggered on low OCR/ASR/verifier confidence or parser ambiguity; user can approve/edit. |
| **Memory** | Stores sessions (input, parsed, context, answer, feedback). Retrieves similar problems for reuse. |



## Repo layout

- **`streamlit_app.py`** – UI; input mode, extraction preview, solve, trace, feedback.
- **`app/config.py`** – Paths, Groq keys, RAG/HITL thresholds.
- **`app/rag.py`** – Build index from `knowledge_base/`, retrieve top-k.
- **`app/embeddings.py`** – Groq embeddings with sentence-transformers fallback.
- **`app/agents/`** – Parser, Router, Solver, Verifier, Explainer.
- **`app/multimodal/ocr.py`** – Vision + EasyOCR. **`app/multimodal/asr.py`** – Whisper.
- **`app/hitl.py`** – `should_trigger_hitl()` conditions.
- **`app/memory.py`** – Store session, retrieve similar.
