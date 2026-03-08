"""Image input: Vision LLM (Groq) first for math symbols, fallback to EasyOCR + LLM fix."""
import base64
from pathlib import Path
from typing import Tuple

from app.config import OCR_CONFIDENCE_THRESHOLD, GROQ_API_KEY, GROQ_VISION_MODEL

_reader = None
VISION_MAX_BYTES = 4 * 1024 * 1024

_VISION_PROMPT = (
    "Extract the math problem from this image as plain text. "
    "Preserve all mathematical notation exactly:\n"
    "- Summation: use Σ (e.g. Σ from i=1 to n, or Σᵢ xᵢ)\n"
    "- Square root: use √\n"
    "- Integrals: use ∫\n"
    "- Fractions: use / or proper fraction layout\n"
    "- Exponents: use ^ or superscript\n"
    "- Greek: π, θ, α, β, etc.\n"
    "Output ONLY the problem text, no explanation. If there is no math problem, say 'No math problem found.'"
)

_LLM_FIX_PROMPT = (
    "The following text was extracted by OCR from a math problem image. "
    "The OCR cannot read math symbols properly — it reads √ as 'V' or 'v', "
    "exponents as separate characters, and garbles special notation.\n\n"
    "Reconstruct the EXACT mathematical expression using proper notation. "
    "Use: √ for square root, ^ for exponents, Σ for summation, ∫ for integral, "
    "π for pi, θ for theta. Keep any non-math text (like 'JEE Main') as-is.\n\n"
    "Output ONLY the corrected mathematical expression, nothing else.\n\n"
    "OCR text: {ocr_text}"
)


def _extract_with_vision(image_path: Path) -> Tuple[str, float]:
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        return "", 0.0
    try:
        data = image_path.read_bytes()
        if len(data) > VISION_MAX_BYTES:
            return "", 0.0
        suffix = image_path.suffix.lower()
        mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png" if suffix == ".png" else "image/jpeg"
        b64 = base64.b64encode(data).decode("utf-8")
        url = f"data:{mime};base64,{b64}"
    except Exception:
        return "", 0.0

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _VISION_PROMPT},
                        {"type": "image_url", "image_url": {"url": url}},
                    ],
                }
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        text = (completion.choices[0].message.content or "").strip()
        if not text or "no math problem found" in text.lower():
            return "", 0.0
        return text, 0.9
    except Exception:
        return "", 0.0


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def _extract_with_easyocr(image_path: Path) -> Tuple[str, float]:
    reader = _get_reader()
    results = reader.readtext(str(image_path))
    if not results:
        return "", 0.0
    texts = []
    confidences = []
    for (_, text, conf) in results:
        if text and isinstance(conf, (int, float)):
            texts.append(text)
            confidences.append(float(conf))
    text = " ".join(texts).strip()
    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return text, mean_conf


def _fix_math_with_llm(ocr_text: str) -> str:
    from app.llm import chat
    prompt = _LLM_FIX_PROMPT.format(ocr_text=ocr_text)
    result = chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=512,
    )
    return result.strip()


def extract_text_from_image(image_path: str | Path) -> Tuple[str, float]:
    path = Path(image_path)
    if not path.exists():
        return "", 0.0

    vision_text, vision_conf = _extract_with_vision(path)
    if vision_text:
        return vision_text, vision_conf
    try:
        raw_text, ocr_conf = _extract_with_easyocr(path)
    except Exception:
        return "", 0.0
    if not raw_text:
        return "", 0.0
    try:
        corrected = _fix_math_with_llm(raw_text)
        if corrected:
            return corrected, ocr_conf
    except Exception:
        pass
    return raw_text, ocr_conf


def ocr_confidence_low(confidence: float) -> bool:
    return confidence < OCR_CONFIDENCE_THRESHOLD
