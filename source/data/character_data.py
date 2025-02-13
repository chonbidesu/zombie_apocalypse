# character_data.py

from collections import namedtuple
from enum import Enum, auto

class Occupation(Enum):
    # Military occupations
    PRIVATE = auto()
    MEDIC = auto()
    SCOUT = auto()

    # Science occupations
    NECROTECH_ASSISTANT = auto()
    DOCTOR = auto()

    # Civilian occupations
    POLICE_OFFICER = auto()
    FIREFIGHTER = auto()
    CONSUMER = auto()

    # Zombie occupations
    CORPSE = auto()

class OccupationCategory(Enum):
    MILITARY = auto()
    SCIENCE = auto()
    CIVILIAN = auto()
    ZOMBIE = auto()

OccupationProperties = namedtuple(
    'OccupationProperties', [
        'occupation', 'occupation_category', 'sprite_sheet', 'description'
    ]
)

OCCUPATIONS = {
    Occupation.PRIVATE: OccupationProperties('Private', OccupationCategory.MILITARY, 'military_sprite_sheet', ''),
    Occupation.MEDIC: OccupationProperties('Medic', OccupationCategory.MILITARY, 'military_sprite_sheet', ''),
    Occupation.SCOUT: OccupationProperties('Scout', OccupationCategory.MILITARY, 'military_sprite_sheet', ''),
    Occupation.NECROTECH_ASSISTANT: OccupationProperties('NecroTech Lab Assistant', OccupationCategory.SCIENCE, 'science_sprite_sheet', ''),
    Occupation.DOCTOR: OccupationProperties('Doctor', OccupationCategory.SCIENCE, 'science_sprite_sheet', ''),
    Occupation.POLICE_OFFICER: OccupationProperties('Police Officer', OccupationCategory.CIVILIAN, 'civilian_sprite_sheet', ''),
    Occupation.FIREFIGHTER: OccupationProperties('Firefighter', OccupationCategory.CIVILIAN, 'civilian_sprite_sheet', ''),
    Occupation.CONSUMER: OccupationProperties('Consumer', OccupationCategory.CIVILIAN, 'consumer_sprite_sheet', ''),
}
