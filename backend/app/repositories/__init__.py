"""Read-only repository classes for approved database tables."""

from app.repositories.base_repository import BaseRepository
from app.repositories.basin_repository import BasinRepository
from app.repositories.nbs_repository import NbsRepository
from app.repositories.plant_repository import PlantRepository
from app.repositories.pollution_repository import PollutionRepository
from app.repositories.region_repository import RegionRepository
from app.repositories.river_repository import RiverRepository
from app.repositories.site_repository import SiteRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.standards_repository import StandardsRepository
from app.repositories.water_repository import WaterRepository

__all__ = [
    "BaseRepository",
    "BasinRepository",
    "NbsRepository",
    "PlantRepository",
    "PollutionRepository",
    "RegionRepository",
    "RiverRepository",
    "SiteRepository",
    "SourceRepository",
    "StandardsRepository",
    "WaterRepository",
]
