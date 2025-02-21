# decision_data.py

from enum import Enum, auto


class Decision(Enum):
    SCOUT_SAFEHOUSE = auto()
    ENTER_SAFEHOUSE = auto()
    BARRICADE_SAFEHOUSE = auto()
    REPAIR_SAFEHOUSE = auto()
    SECURE_SAFEHOUSE = auto()
    POWER_SAFEHOUSE = auto()
    DEFEND_SAFEHOUSE = auto()
    RETREAT_TO_SAFEHOUSE = auto()

    HUNT = auto()
    PATROL = auto()
    ATTACK_TO_KILL = auto()
    ARM_THYSELF = auto()
    HEAL_THYSELF = auto()
    FLEE = auto()
    DUMP_BODIES = auto()

    SEEK_ITEMS = auto()
    SEEK_WEAPON = auto()
    SEEK_AMMO = auto()
    SEEK_FAK = auto()
    PURGE_ITEMS = auto()