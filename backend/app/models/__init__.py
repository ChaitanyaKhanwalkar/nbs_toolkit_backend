"""Database model definitions that mirror the approved schema."""

from app.models.basin import Basin
from app.models.nbs_criteria import NbsCriteria
from app.models.nbs_footprint import NbsFootprint
from app.models.nbs_implementation import NbsImplementation
from app.models.nbs_option import NbsOption
from app.models.plant import Plant
from app.models.plant_solution_map import PlantSolutionMap
from app.models.pollution_source import PollutionSource
from app.models.region import Region
from app.models.removal_efficiency import RemovalEfficiency
from app.models.river_network import RiverNetwork
from app.models.site_attribute import SiteAttribute
from app.models.site_stream_attribute import SiteStreamAttribute
from app.models.source import Source
from app.models.standard import Standard
from app.models.water_observation import WaterObservation
from app.models.water_type_profile import WaterTypeProfile

__all__ = [
    "Basin",
    "NbsCriteria",
    "NbsFootprint",
    "NbsImplementation",
    "NbsOption",
    "Plant",
    "PlantSolutionMap",
    "PollutionSource",
    "Region",
    "RemovalEfficiency",
    "RiverNetwork",
    "SiteAttribute",
    "SiteStreamAttribute",
    "Source",
    "Standard",
    "WaterObservation",
    "WaterTypeProfile",
]
