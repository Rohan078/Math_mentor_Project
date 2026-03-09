"""
Math Mentor - Streamlit UI
Multimodal (Text / Image / Audio) → RAG + Agents + HITL + Memory
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env", override=True)

from app.config import KNOWLEDGE_BASE_DIR, DATA_DIR
from app.rag import build_index, retrieve
from app.agents.parser import parse_problem, ParsedProblem
from app.agents.router import route_intent, IntentResult
from app.agents.solver import solve_problem, SolverResult
from app.agents.verifier import verify_solution, VerificationResult
from app.agents.explainer import explain_solution, ExplainerResult
from app.multimodal.ocr import extract_text_from_image, ocr_confidence_low
from app.multimodal.asr import transcribe_audio, asr_confidence_low
from app.hitl import should_trigger_hitl
from app.memory import store, retrieve_similar, get_correction_rules

try:
    from groq import AuthenticationError as GroqAuthError
except Exception:
    GroqAuthError = Exception

st.set_page_config(page_title="Math Mentor", layout="wide")
st.title("AI Math Mentor")
st.caption("JEE-style math: Algebra, Probability, Calculus, Linear Algebra. Multimodal input + RAG + Agents + HITL + Memory.")

if "trace" not in st.session_state:
    st.session_state.trace = []
if "result" not in st.session_state:
    st.session_state.result = None
if "hitl_triggered" not in st.session_state:
    st.session_state.hitl_triggered = False
if "extraction_preview" not in st.session_state:
    st.session_state.extraction_preview = ""
if "extraction_confidence" not in st.session_state:
    st.session_state.extraction_confidence = 1.0
if "input_type" not in st.session_state:
    st.session_state.input_type = "text"
if "raw_input" not in st.session_state:
    st.session_state.raw_input = ""
if "show_incorrect_form" not in st.session_state:
    st.session_state.show_incorrect_form = False


def add_trace(agent: str, detail: str):
    st.session_state.trace.append({"agent": agent, "detail": detail})


st.sidebar.header("Input mode")
input_mode = st.sidebar.radio("Choose input", ["Text", "Image", "Audio"], index=0)
st.session_state.input_type = input_mode.lower()

with st.sidebar:
    from app.config import GROQ_API_KEY as _key
    _key_ok = bool(_key and _key != "your_groq_api_key_here")
    if _key_ok:
        st.success(f"Groq API key loaded (length {len(_key)})")
    else:
        st.error("Groq API key missing or placeholder. Edit `.env` and add GROQ_API_KEY=gsk_...")
    if st.button("Rebuild knowledge base (RAG)"):
        with st.spinner("Building index..."):
            build_index(force_rebuild=True)
        st.success("Index rebuilt.")
    st.info("Knowledge base: " + str(KNOWLEDGE_BASE_DIR))

raw_text = ""
source_hint = "text"
ocr_conf = None
asr_conf = None

if input_mode == "Text":
    raw_text = st.text_area("Type your math question", height=120, placeholder="e.g. Solve x² - 5x + 6 = 0")
    st.session_state.raw_input = raw_text
    if raw_text:
        st.session_state.extraction_preview = raw_text
        st.session_state.extraction_confidence = 1.0

elif input_mode == "Image":
    uploaded = st.file_uploader("Upload problem image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    st.caption("Uses Groq Vision LLM for math symbols (Σ, √, ∫); falls back to EasyOCR if needed.")
    if uploaded:
        file_id = (uploaded.name, uploaded.size)
        if st.session_state.get("_ocr_file_id") != file_id:
            temp_path = DATA_DIR / f"upload_{uploaded.name}"
            temp_path.write_bytes(uploaded.getvalue())
            ocr_text, ocr_conf_val = extract_text_from_image(temp_path)
            st.session_state._ocr_file_id = file_id
            st.session_state._ocr_file = uploaded.name
            st.session_state._ocr_text = ocr_text or ""
            st.session_state._ocr_conf = ocr_conf_val
            st.session_state.result = None
            st.session_state.trace = []
        st.image(uploaded, use_container_width=True, caption="Uploaded image")
    else:
        if "_ocr_file_id" in st.session_state:
            for k in ("_ocr_file_id", "_ocr_file", "_ocr_text", "_ocr_conf"):
                st.session_state.pop(k, None)
            st.session_state.result = None
            st.session_state.trace = []

    if st.session_state.get("_ocr_text") is not None:
        ocr_conf = st.session_state.get("_ocr_conf", 1.0)
        st.session_state.extraction_confidence = ocr_conf
        st.session_state.extraction_preview = st.session_state._ocr_text or "(No text detected)"
        source_hint = "ocr"
        st.subheader("Extracted text (edit if needed)")
        raw_text = st.text_area("OCR preview", value=st.session_state._ocr_text, height=100, key="ocr_edit")
        st.session_state.raw_input = raw_text
        st.caption(f"OCR confidence: {ocr_conf:.2f}" + (" ⚠️ Low — please confirm" if ocr_confidence_low(ocr_conf) else ""))

elif input_mode == "Audio":
    audio_source = st.radio("Audio source", ["Record from microphone", "Upload audio file"], horizontal=True, key="audio_src")
    if st.button("New question (clear transcript & record/upload again)", key="audio_new_q"):
        for k in ("_asr_mic_id", "_asr_file_id", "_asr_file", "_asr_text", "_asr_conf"):
            st.session_state.pop(k, None)
        st.session_state.result = None
        st.session_state.trace = []
        st.rerun()
    if audio_source == "Record from microphone":
        try:
            from st_audiorec import st_audiorec
            wav_bytes = st_audiorec()
            if wav_bytes and isinstance(wav_bytes, bytes) and len(wav_bytes) >= 44:
                mic_id = hash(wav_bytes)
                if st.session_state.get("_asr_mic_id") != mic_id:
                    mic_path = DATA_DIR / "mic_recording.wav"
                    mic_path.write_bytes(wav_bytes)
                    with st.spinner("Transcribing..."):
                        asr_text, asr_conf_val = transcribe_audio(mic_path)
                    st.session_state._asr_mic_id = mic_id
                    st.session_state._asr_file = "mic"
                    st.session_state._asr_text = asr_text or ""
                    st.session_state._asr_conf = asr_conf_val
                    st.session_state.result = None
                    st.session_state.trace = []
            elif wav_bytes is not None and (not isinstance(wav_bytes, bytes) or len(wav_bytes) < 44):
                st.warning("Recording too short or invalid. Record at least 1–2 seconds of speech, then stop.")
        except Exception as e:
            st.warning(f"Mic recording not available: {e}. Install: pip install streamlit-audiorec")
    else:
        uploaded_audio = st.file_uploader("Upload audio (e.g. MP3, WAV)", type=["mp3", "wav", "m4a", "ogg", "webm"], key="audio_upload")
        if uploaded_audio:
            file_id = (uploaded_audio.name, uploaded_audio.size)
            if st.session_state.get("_asr_file_id") != file_id:
                temp_path = DATA_DIR / f"audio_{uploaded_audio.name}"
                temp_path.write_bytes(uploaded_audio.getvalue())
                asr_text, asr_conf_val = transcribe_audio(temp_path)
                st.session_state._asr_file_id = file_id
                st.session_state._asr_file = uploaded_audio.name
                st.session_state._asr_text = asr_text or ""
                st.session_state._asr_conf = asr_conf_val
                st.session_state.result = None
                st.session_state.trace = []
        else:
            if "_asr_file_id" in st.session_state or "_asr_text" in st.session_state:
                for k in ("_asr_file_id", "_asr_file", "_asr_text", "_asr_conf"):
                    st.session_state.pop(k, None)
                st.session_state.result = None
                st.session_state.trace = []

    if st.session_state.get("_asr_text") is not None:
        asr_conf = st.session_state.get("_asr_conf", 1.0)
        st.session_state.extraction_confidence = asr_conf
        st.session_state.extraction_preview = st.session_state._asr_text or "(No speech detected)"
        source_hint = "asr"
        st.subheader("Transcript (edit if needed)")
        raw_text = st.text_area(
            "ASR preview",
            value=st.session_state._asr_text,
            height=100,
            key="asr_edit",
            placeholder="If no transcript appeared, type your math question here.",
        )
        st.session_state.raw_input = raw_text
        if not (st.session_state._asr_text or "").strip():
            st.info("No transcript yet. Type your math question in the box above, or record again (speak clearly, then stop).")
        st.caption(f"Transcription confidence: {asr_conf:.2f}" + (" ⚠️ Please confirm" if asr_confidence_low(asr_conf) else ""))

if st.button("Solve", type="primary") and raw_text:
    st.session_state.trace = []
    st.session_state.show_incorrect_form = False
    add_trace("System", "Starting pipeline")

    try:
        try:
            build_index(force_rebuild=False)
        except Exception:
            build_index(force_rebuild=True)

        add_trace("Parser Agent", "Cleaning and structuring problem")
        parsed = parse_problem(raw_text, source_hint=source_hint)
        add_trace("Parser Agent", f"Topic: {parsed.topic}, needs_clarification: {parsed.needs_clarification}")

        hitl, hitl_reason = should_trigger_hitl(
            ocr_confidence=ocr_conf if input_mode == "Image" else None,
            asr_confidence=asr_conf if input_mode == "Audio" else None,
            needs_clarification=parsed.needs_clarification,
            user_requested_recheck=False,
        )
        if hitl and (parsed.needs_clarification or (input_mode != "Text" and (ocr_conf or asr_conf or 0) < 0.7)):
            st.session_state.hitl_triggered = True
            st.warning(f"Human-in-the-loop: {hitl_reason}")
            st.info("Please edit the extracted text above if needed, then click Solve again. Or confirm and proceed.")
            add_trace("HITL", hitl_reason)

        # Memory at runtime: retrieve similar solved problems, reuse solution patterns, apply OCR/audio correction rules (no retraining)
        similar = retrieve_similar(parsed.problem_text, top_k=2)
        correction_rules = get_correction_rules(limit=10)
        if similar:
            add_trace("Memory", f"Found {len(similar)} similar past solution(s)")
        if correction_rules:
            add_trace("Memory", f"Using {len(correction_rules)} past correction(s) to improve answer")

        add_trace("Intent Router", "Classifying problem and choosing strategy")
        intent = route_intent(parsed)
        add_trace("Intent Router", f"Intent: {intent.intent}, Strategy: {intent.strategy}")

        add_trace("Solver Agent", "Retrieving context and solving (with past feedback)")
        solver_result = solve_problem(parsed, intent, similar_sessions=similar, correction_rules=correction_rules)
        add_trace("Solver Agent", f"Answer found. Context chunks used: {len(solver_result.context_used)}")

        add_trace("Verifier Agent", "Checking correctness and confidence")
        verification = verify_solution(parsed, solver_result)
        add_trace("Verifier Agent", f"Correct: {verification.is_correct}, Confidence: {verification.confidence:.2f}")

        if verification.hitl_required:
            st.session_state.hitl_triggered = True
            st.warning("Verifier suggests human review (low confidence).")

        add_trace("Explainer Agent", "Generating step-by-step explanation")
        explainer_result = explain_solution(parsed, solver_result)

        st.session_state.result = {
            "parsed": parsed,
            "intent": intent,
            "solver_result": solver_result,
            "verification": verification,
            "explainer_result": explainer_result,
            "retrieved_context": solver_result.context_used,
            "similar_memory": similar,
        }

    except GroqAuthError:
        st.error(
            "**Invalid Groq API key (401).** Check your `.env` file:\n\n"
            "• Open `.env` in the project folder and ensure the line is exactly:\n  `GROQ_API_KEY=gsk_...`\n\n"
            "• No quotes, no extra spaces, no line break in the key.\n\n"
            "• Get a valid key at [console.groq.com](https://console.groq.com/) → API Keys.\n\n"
            "• Restart the app after changing `.env`."
        )
        st.session_state.trace.append({"agent": "Error", "detail": "Invalid API key"})

if st.session_state.result:
    r = st.session_state.result
    parsed = r["parsed"]
    solver_result = r["solver_result"]
    verification = r["verification"]
    explainer_result = r["explainer_result"]

    st.divider()
    with st.expander("Agent trace (what ran and why)", expanded=True):
        for t in st.session_state.trace:
            st.markdown(f"- **{t['agent']}**: {t['detail']}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Retrieved context (RAG)")
        if r["retrieved_context"]:
            for i, c in enumerate(r["retrieved_context"]):
                st.caption(f"Source: {c.get('source', '?')}")
                st.text(c.get("content", "")[:400] + ("..." if len(c.get("content", "")) > 400 else ""))
        else:
            st.caption("No retrieved chunks (empty index or no match).")

    with col2:
        st.subheader("Final answer")
        st.markdown(f"**{solver_result.answer}**")
        st.subheader("Confidence")
        conf = max(0.0, min(1.0, float(verification.confidence)))
        pct = min(100, max(0, int(round(conf * 100))))
        st.progress(pct)
        st.caption(f"{conf:.0%}")
        if verification.issues:
            st.caption("Issues: " + "; ".join(verification.issues))

    st.subheader("Step-by-step explanation")
    st.markdown(explainer_result.explanation)

    st.divider()
    st.subheader("Feedback")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ Correct"):
            store(
                input_type=st.session_state.input_type,
                raw_input=st.session_state.raw_input,
                parsed_question={"problem_text": parsed.problem_text, "topic": parsed.topic, "variables": parsed.variables, "constraints": parsed.constraints},
                retrieved_context=solver_result.context_used,
                final_answer=solver_result.answer,
                steps=solver_result.steps,
                verifier_outcome={"is_correct": verification.is_correct, "confidence": verification.confidence},
                user_feedback="correct",
            )
            st.success("Thanks! Stored as correct.")
    with col_b:
        if st.button("❌ Incorrect"):
            st.session_state.show_incorrect_form = True
    if st.session_state.show_incorrect_form:
        comment = st.text_input("Comment (what was wrong?)", key="fb_comment")
        corrected = st.text_input("Correct answer (optional)", key="fb_corrected")
        if st.button("Submit feedback"):
            store(
                input_type=st.session_state.input_type,
                raw_input=st.session_state.raw_input,
                parsed_question={"problem_text": parsed.problem_text, "topic": parsed.topic},
                retrieved_context=solver_result.context_used,
                final_answer=solver_result.answer,
                steps=solver_result.steps,
                verifier_outcome={"is_correct": False, "confidence": verification.confidence},
                user_feedback="incorrect",
                user_comment=comment or None,
                corrected_answer=corrected or None,
            )
            st.success("Thanks! We'll learn from this.")
            st.session_state.show_incorrect_form = False
            st.rerun()

if st.sidebar.button("Request re-check (HITL)"):
    st.session_state.hitl_triggered = True
    st.sidebar.info("Re-check requested. Run Solve again after editing input if needed.")

st.sidebar.divider()
if not os.getenv("GROQ_API_KEY"):
    st.sidebar.error("Set GROQ_API_KEY in .env to use the app.")
