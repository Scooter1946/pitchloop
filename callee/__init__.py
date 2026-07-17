"""Deterministic callee oracle for fake mode and conformance tests."""

from .call_harness import RubricResult, evaluate_pitch, normalize_for_match

__all__ = ["RubricResult", "evaluate_pitch", "normalize_for_match"]
