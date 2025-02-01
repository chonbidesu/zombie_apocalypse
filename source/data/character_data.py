# character_data.py

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


HUMAN_OCCUPATIONS = [
    Occupation.PRIVATE,
    Occupation.MEDIC,
    Occupation.SCOUT,
    Occupation.NECROTECH_ASSISTANT,
    Occupation.DOCTOR,
    Occupation.POLICE_OFFICER,
    Occupation.FIREFIGHTER,
    Occupation.CONSUMER,
]