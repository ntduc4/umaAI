from __future__ import annotations


class GameToraCardRepository:
    """Future adapter for fetching support-card stats by card and level."""

    def get_card(self, card_name: str, level: int):
        raise NotImplementedError("GameTora card ingestion is planned but not implemented yet")
