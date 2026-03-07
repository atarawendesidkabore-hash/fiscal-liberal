"""Dedicated Art. 145 checker wrapper."""

from __future__ import annotations

from .is_calculator import ISCalculator


class MereFilialeService:
    def __init__(self) -> None:
        self._calculator = ISCalculator()

    def verifier(self, participation: dict) -> dict:
        return self._calculator.verifier_mere_filiale(participation)

