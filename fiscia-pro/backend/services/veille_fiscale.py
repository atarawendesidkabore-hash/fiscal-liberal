"""Fiscal monitoring service placeholder for legal sources polling."""

from __future__ import annotations


class VeilleFiscaleService:
    def list_sources(self) -> list[str]:
        return [
            "LFI/LFR",
            "Conseil d'Etat",
            "BOFiP",
            "Reglements UE (DAC6/DAC7/Pilier 2/ViDA)",
        ]

