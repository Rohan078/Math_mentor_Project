"""Human-in-the-loop: trigger conditions."""
from typing import Optional


def should_trigger_hitl(
    ocr_confidence: Optional[float] = None,
    asr_confidence: Optional[float] = None,
    needs_clarification: bool = False,
    verifier_confidence: Optional[float] = None,
    verifier_hitl_required: bool = False,
    user_requested_recheck: bool = False,
    ocr_threshold: float = 0.6,
    asr_threshold: float = 0.7,
    verifier_threshold: float = 0.7,
) -> tuple[bool, str]:
    if user_requested_recheck:
        return True, "User requested re-check"
    if needs_clarification:
        return True, "Parser detected ambiguity or missing information"
    if ocr_confidence is not None and ocr_confidence < ocr_threshold:
        return True, "OCR confidence low — please confirm or edit extracted text"
    if asr_confidence is not None and asr_confidence < asr_threshold:
        return True, "Transcription confidence low — please confirm or edit transcript"
    if verifier_hitl_required or (verifier_confidence is not None and verifier_confidence < verifier_threshold):
        return True, "Verifier not confident — please review solution"
    return False, ""
