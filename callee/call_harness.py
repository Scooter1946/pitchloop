"""Pure, deterministic pitch evaluator used as the fake callee oracle."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


REJECTED_MISSING_FACT_A_RESPONSE = (
    "That is too generic and does not show that you understand what is relevant "
    "to us. I am not taking the meeting."
)
REJECTED_MISSING_FACT_B_RESPONSE = (
    "That first point is relevant, but you have not shown that you understand our "
    "August 30 API v1 migration deadline. I am not taking the meeting."
)
MEETING_BOOKED_RESPONSE = (
    "Yes, that is relevant to what we are doing. Send me a 20-minute invite for "
    "Tuesday at 2 PM."
)


@dataclass(frozen=True, slots=True)
class RubricResult:
    status: str
    code: str
    missing_claims: tuple[str, ...]
    response: str


def normalize_for_match(value: str) -> str:
    """Normalize Unicode, punctuation, whitespace, and case for matching."""

    if not isinstance(value, str):
        raise TypeError("value must be a string")
    decomposed = unicodedata.normalize("NFKD", value).casefold()
    without_marks = "".join(
        char for char in decomposed if not unicodedata.category(char).startswith("M")
    )
    punctuation_as_space = "".join(
        " " if unicodedata.category(char)[0] in {"P", "S"} else char
        for char in without_marks
    )
    return re.sub(r"\s+", " ", punctuation_as_space).strip()


def _contains_normalized(text: str, expected: str) -> bool:
    normalized_expected = normalize_for_match(expected)
    return bool(normalized_expected) and normalized_expected in normalize_for_match(text)


def evaluate_pitch(
    pitch_text: str,
    fact_a_statement: str,
    fact_b_phrase: str,
) -> RubricResult:
    """Apply the frozen rubric in precedence order without semantic scoring."""

    if not _contains_normalized(pitch_text, fact_a_statement):
        return RubricResult(
            status="rejected",
            code="REJECTED_MISSING_FACT_A",
            missing_claims=("fact_a",),
            response=REJECTED_MISSING_FACT_A_RESPONSE,
        )
    if not _contains_normalized(pitch_text, fact_b_phrase):
        return RubricResult(
            status="rejected",
            code="REJECTED_MISSING_FACT_B",
            missing_claims=("fact_b",),
            response=REJECTED_MISSING_FACT_B_RESPONSE,
        )
    return RubricResult(
        status="booked",
        code="MEETING_BOOKED",
        missing_claims=(),
        response=MEETING_BOOKED_RESPONSE,
    )
