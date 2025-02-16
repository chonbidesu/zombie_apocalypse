# character_data.py

from collections import namedtuple
from enum import Enum, auto
from data.skill_data import SkillType

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
        'occupation', 'occupation_category', 'sprite_sheet', 'starting_skill', 'starting_items', 'description',
    ]
)

OCCUPATIONS = {
    Occupation.PRIVATE: OccupationProperties('Private', OccupationCategory.MILITARY, 'military_sprite_sheet', SkillType.BASIC_FIREARMS_TRAINING, ['PISTOL', 'PISTOL_CLIP'],
                                             'Starts with basic firearms training, a pistol and spare ammunition.'),
    Occupation.MEDIC: OccupationProperties('Medic', OccupationCategory.MILITARY, 'military_sprite_sheet', SkillType.FIRST_AID, ['FIRST_AID_KIT', 'PISTOL'],
                                           'Starts with first-aid training, a medical kit and a pistol.'),
    Occupation.SCOUT: OccupationProperties('Scout', OccupationCategory.MILITARY, 'military_sprite_sheet', SkillType.FREE_RUNNING, ['BINOCULARS'],
                                           'Can move between adjacent buildings without stopping outside. Carries a pair of binoculars.'),
    Occupation.NECROTECH_ASSISTANT: OccupationProperties('NecroTech Lab Assistant', OccupationCategory.SCIENCE, 'science_sprite_sheet', SkillType.NECROTECH_EMPLOYMENT, ['DNA_EXTRACTOR'],
                                                         'Starts with a DNA Extractor, and is able to recognise NecroTech laboratories from the street.'),
    Occupation.DOCTOR: OccupationProperties('Doctor', OccupationCategory.SCIENCE, 'science_sprite_sheet', SkillType.DIAGNOSIS, ['FIRST_AID_KIT', 'FIRST_AID_KIT'],
                                            "Can diagnose others' injuries, and carries two first-aid kits."),
    Occupation.POLICE_OFFICER: OccupationProperties('Police Officer', OccupationCategory.CIVILIAN, 'civilian_sprite_sheet', SkillType.BASIC_FIREARMS_TRAINING, ['PISTOL', 'PISTOL_CLIP'],
                                                    'Starts with basic firearms training, a pistol and spare ammunition.'),
    Occupation.FIREFIGHTER: OccupationProperties('Firefighter', OccupationCategory.CIVILIAN, 'civilian_sprite_sheet', SkillType.AXE_PROFICIENCY, ['FIRE_AXE', 'FIRST_AID_KIT'],
                                                 'Starts with a fire axe and a first-aid kit, and axe-handling training.'),
    Occupation.CONSUMER: OccupationProperties('Consumer', OccupationCategory.CIVILIAN, 'consumer_sprite_sheet', SkillType.SHOPPING, ['GOLF_CLUB'],
                                              'Knows where specific stores are, when looting malls. Carries a random improvised weapon.'),
    Occupation.CORPSE: OccupationProperties('Corpse', OccupationCategory.ZOMBIE, 'zombie_sprite_sheet', SkillType.VIGOUR_MORTIS, [],
                                            "Rigor mortis has given you stronger attacks. By starting the game as a zombie, you'll start off more effective in combat than survivors who become zombies later in the game."),
}
