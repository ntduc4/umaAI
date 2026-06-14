from __future__ import annotations

from uma_ai.career.models import TurnLogEntry


class TurnLogger:
    """Future persistent logger for every observed and simulated turn."""

    def write(self, entry: TurnLogEntry) -> None:
        raise NotImplementedError("persistent turn logging is planned but not implemented yet")
