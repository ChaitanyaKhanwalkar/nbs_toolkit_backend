"""Read-only repository for pollution pressure records.

Use this repository to fetch and lightly group raw pollution source rows. The
grouping method is not a score, rank, or scientific interpretation.
"""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PollutionSource
from app.repositories.base_repository import BaseRepository


class PollutionRepository(BaseRepository):
    """Read helpers for pollution source records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_pollution_sources(self, region_id: int) -> list[PollutionSource]:
        """Return raw pollution source rows for one region."""

        statement = (
            select(PollutionSource)
            .where(PollutionSource.region_id == region_id)
            .order_by(PollutionSource.source_type, PollutionSource.category)
        )
        return list(self.session.scalars(statement).all())

    def summarize_pollution_pressure(self, region_id: int) -> list[dict[str, object]]:
        """Group raw pollution rows by source type/category/indicator.

        This method only organizes raw data for display or service use. It does
        not calculate severity, risk, or suitability scores.
        """

        grouped: dict[tuple[str | None, str | None, str | None], list[PollutionSource]]
        grouped = defaultdict(list)
        for row in self.get_pollution_sources(region_id):
            key = (row.source_type, row.category, row.indicator)
            grouped[key].append(row)

        summaries: list[dict[str, object]] = []
        for (source_type, category, indicator), rows in grouped.items():
            summaries.append(
                {
                    "source_type": source_type,
                    "category": category,
                    "indicator": indicator,
                    "count": len(rows),
                    "values": [
                        {
                            "value": row.value,
                            "unit": row.unit,
                            "note": row.note,
                            "source_id": row.source_id,
                        }
                        for row in rows
                    ],
                }
            )
        return summaries
