# Math Mentor – Multimodal RAG + Agents + HITL + Memory

JEE-style math mentor: **Algebra**, **Probability**, **Calculus**, **Linear algebra**. Accepts **text**, **image** (OCR), and **audio** (ASR), runs a **RAG pipeline** and **multi-agent system**, supports **human-in-the-loop** and **memory** for learning.

## Features

- **Multimodal input**: Type, upload image (JPG/PNG), or upload audio (MP3/WAV). OCR (EasyOCR) and ASR (Whisper) with editable preview and low-confidence → HITL.
- **Parser agent**: Cleans and structures problem (topic, variables, constraints, `needs_clarification`).
- **RAG**: Curated knowledge base (15+ docs), Chroma + Groq or sentence-transformers embeddings, top-k retrieval, sources shown in UI (no hallucinated citations when retrieval fails).
- **Agents**: Parser, Intent Router, Solver (RAG + optional Python calc), Verifier/Critic, Explainer/Tutor.
- **HITL**: Triggered on low OCR/ASR confidence, parser ambiguity, verifier low confidence, or user “re-check”. Approve/edit/reject; corrections stored as learning signals.
- **Memory**: Stores input, parsed question, context, answer, verifier outcome, feedback. Similar-problem retrieval and correction rules for reuse.

## Deliverables

| Item | Link |
|------|------|
| **Live app** | _Add your Streamlit Cloud URL_ |
| **Demo video (3–5 min)** | _Add YouTube / Loom link: image → solution, audio → solution, HITL, memory reuse_ |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) (Mermaid diagrams) |
| **Evaluation** | [EVALUATION.md](EVALUATION.md) |
| **Checklist** | [DELIVERABLES.md](DELIVERABLES.md) |

## Setup

### 1. Clone and install

```bash
cd Math_mentor_Project
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. API key (Groq – free)

1. Get a key at [console.groq.com](https://console.groq.com/).
2. Copy `.env.example` to `.env` and set:
   ```
   GROQ_API_KEY=your_key_here
   ```

### 3. Optional: ffmpeg (for Whisper ASR)

- **Windows**: `choco install ffmpeg` or download from ffmpeg.org.
- **macOS**: `brew install ffmpeg`.
- **Linux**: `sudo apt install ffmpeg`.

### 4. Build RAG index (first time)

```bash
python build_rag.py
```

Or use the **“Rebuild knowledge base (RAG)”** button in the app sidebar.

### 5. Run the app

```bash
streamlit run streamlit_app.py
```

Open the URL shown (e.g. http://localhost:8501).

## UI overview

- **Input mode**: Text / Image / Audio.
- **Extraction preview**: OCR or transcript with confidence; edit before solving.
- **Agent trace**: What ran and why (Parser → Router → Solver → Verifier → Explainer).
- **Retrieved context**: RAG chunks and sources.
- **Final answer + explanation**: With confidence indicator.
- **Feedback**: ✅ Correct / ❌ Incorrect + comment (and optional corrected answer). Stored in memory.

## Deployment

**This app is Streamlit (long-running server), so it does not run on Vercel** (Vercel is serverless). Use **Streamlit Community Cloud** or **Hugging Face Spaces** instead. See **[DEPLOYMENT.md](DEPLOYMENT.md)** for full steps and why Vercel isn’t used.

**Quick: Streamlit Community Cloud**

1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo.
3. Set **Root directory** to the project folder (e.g. `Math_mentor_Project` if in a monorepo) or leave blank if repo root is the project.
4. **Main file**: `streamlit_app.py`.
5. **Secrets**: add `GROQ_API_KEY` in Streamlit Cloud secrets.
6. **Python version**: 3.10 or 3.11 recommended.
7. Optional: add `packages.txt` for system deps (e.g. `ffmpeg` if needed; Cloud may have it).

Example `packages.txt` (if required by platform):

```
# packages.txt (only if your host needs it)
# ffmpeg
```

Streamlit Cloud often provides ffmpeg. If EasyOCR/Whisper are heavy, consider:
- Using **tiny** Whisper model (already set in code).
- Or disabling Image/Audio in deployment and keeping only Text + RAG + agents.

## Project structure

```
Math_mentor_Project/
  .env                    # GROQ_API_KEY (create from .env.example)
  requirements.txt
  streamlit_app.py        # Main Streamlit UI
  build_rag.py            # Build RAG index
  app/
    config.py
    llm.py                # Groq chat
    embeddings.py         # Groq or sentence-transformers
    rag.py                # Chroma RAG
    memory.py             # Memory layer
    hitl.py               # HITL conditions
    agents/
      parser.py
      router.py
      solver.py
      verifier.py
      explainer.py
    multimodal/
      ocr.py              # EasyOCR
      asr.py              # Whisper
  knowledge_base/         # 15+ .md docs for RAG
  data/                   # Chroma DB, memory.jsonl, uploads
```

## Scope

- **Math**: Algebra, probability, basic calculus (limits, derivatives, optimization), linear algebra basics (JEE-level, not olympiad).
- **No model retraining**: Memory uses pattern reuse and correction rules only.

## License

MIT.
