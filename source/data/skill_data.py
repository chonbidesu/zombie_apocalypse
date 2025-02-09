# skill_data.py

from enum import Enum, auto
from collections import namedtuple

class SkillType(Enum):
    # Civilian skills
    SHOPPING = auto()
    BARGAIN_HUNTING = auto()
    BODY_BUILDING = auto()
    CONSTRUCTION = auto()

    # Military skills
    BASIC_FIREARMS_TRAINING = auto()
    PISTOL_TRAINING = auto()
    ADV_PISTOL_TRAINING = auto()
    SHOTGUN_TRAINING = auto()
    ADV_SHOTGUN_TRAINING = auto()
    HAND_TO_HAND = auto()
    KNIFE_COMBAT = auto()
    AXE_PROFICIENCY = auto()
    FREE_RUNNING = auto()

    # Science skills
    NECROTECH_EMPLOYMENT = auto()
    LAB_EXPERIENCE = auto()
    NECRONET_ACCESS = auto()
    FIRST_AID = auto()
    SURGERY = auto()
    DIAGNOSIS = auto()

    # Zombie Hunter skills
    HEADSHOT = auto()

    # Zombie skills
    SCENT_FEAR = auto()
    SCENT_BLOOD = auto()
    SCENT_TRAIL = auto()
    SCENT_DEATH = auto()
    DIGESTION = auto()
    INFECTIOUS_BITE = auto()
    VIGOUR_MORTIS = auto()
    NECK_LURCH = auto()
    DEATH_GRIP = auto()
    REND_FLESH = auto()
    TANGLING_GRASP = auto()
    FEEDING_DRAG = auto()
    MEMORIES_OF_LIFE = auto()
    FEEDING_GROAN = auto()
    RANSACK = auto()
    LURCHING_GAIT = auto()
    ANKLE_GRAB = auto()
    BRAIN_ROT = auto()
    FLESH_ROT = auto()


class SkillCategory(Enum):
    CIVILIAN = auto()
    MILITARY = auto()
    SCIENCE = auto()
    ZOMBIE_HUNTER = auto()
    ZOMBIE = auto()

SkillProperties = namedtuple(
    'SkillProperties', [
        'skill_type', 'skill_category', 'description',
    ]
)

SKILLS = {
    SkillType.SHOPPING: SkillProperties('Shopping', SkillCategory.CIVILIAN, 
                                        'Player may choose which stores to loot, when searching a mall. The Consumer class starts with this skill. Widely considered to be essential for searching in malls to be effective.'),
    SkillType.BARGAIN_HUNTING: SkillProperties('Bargain Hunting', SkillCategory.CIVILIAN, 
                                               'Player has +25% of having a successful search inside of a Mall. Shopping is required before Bargain Hunting may be purchased.'),
    SkillType.BODY_BUILDING: SkillProperties('Body Building', SkillCategory.CIVILIAN, 
                                             'Grants an additional 10 Max Hit points, for a total of 60 Max HP.'),
    SkillType.CONSTRUCTION: SkillProperties('Construction', SkillCategory.CIVILIAN, 
                                            'Player is able to barricade buildings, and repair buildings which have been ruined and generators which have been damaged. Repairing buildings or generators requires the use of a Toolbox.'),
    SkillType.BASIC_FIREARMS_TRAINING: SkillProperties('Basic Firearms Training', SkillCategory.MILITARY, 
                                                       'Player gets +25% to hit with all ranged weapon attacks. The Private and Police Officer start with this skill.'),
    SkillType.PISTOL_TRAINING: SkillProperties('Pistol Training', SkillCategory.MILITARY, 
                                               'An extra +25% to hit with a pistol.'),
    SkillType.ADV_PISTOL_TRAINING: SkillProperties('Advanced Pistol Training', SkillCategory.MILITARY, 
                                                   'An extra +10% to hit with a pistol.'),
    SkillType.SHOTGUN_TRAINING: SkillProperties('Shotgun Training', SkillCategory.MILITARY, 
                                                'An extra +25% to hit with a shotgun.'),
    SkillType.ADV_SHOTGUN_TRAINING: SkillProperties('Advanced Shotgun Training', SkillCategory.MILITARY, 
                                                    'An extra +10% to hit with a shotgun.'),
    SkillType.HAND_TO_HAND: SkillProperties('Hand-to-Hand Combat', SkillCategory.MILITARY, 
                                            'Player gets +15% to hit with melee weapon attacks or fists.'),
    SkillType.KNIFE_COMBAT: SkillProperties('Knife Combat', SkillCategory.MILITARY, 
                                            'An extra +15% to hit with a knife.'),
    SkillType.AXE_PROFICIENCY: SkillProperties('Axe Proficiency', SkillCategory.MILITARY, 
                                               'An extra +15% to hit with an axe. The Firefighter begins with this skill.'),
    SkillType.FREE_RUNNING: SkillProperties('Free Running', SkillCategory.MILITARY, 
                                            'Free Running allows a player to move from inside a building directly into an adjacent building without having to touch the street. This allows a player to bypass heavy barricades which would otherwise prevent entry. The Scout begins with this skill.'),
    SkillType.NECROTECH_EMPLOYMENT: SkillProperties('NecroTech Employment', SkillCategory.SCIENCE, 
                                                    'Player is able to operate DNA Extractors, and can identify NecroTech offices from the street. Starting skill for the NecroTech Lab Assistant class.'),
    SkillType.LAB_EXPERIENCE: SkillProperties('Lab Experience', SkillCategory.SCIENCE, 
                                              'Can recognise and operate basic-level NecroTech equipment. Required skill for reviving a zombie with a revivification syringe.'),
    SkillType.NECRONET_ACCESS: SkillProperties('NecroNet Access', SkillCategory.SCIENCE, 
                                               'Player can access terminals in powered NT buildings, allowing map scans, syringe manufacture, and reviving zombies with Brain Rot.'),
    SkillType.FIRST_AID: SkillProperties('First Aid', SkillCategory.SCIENCE, 
                                         'Player is able to heal an extra 5 HP when using a First Aid Kit. Starting skill for the Medic class.'),
    SkillType.SURGERY: SkillProperties('Surgery', SkillCategory.SCIENCE, 
                                       'Player can heal a further 5 HP with a first aid kit if working in a hospital or infirmary with power.'),
    SkillType.DIAGNOSIS: SkillProperties('Diagnosis', SkillCategory.SCIENCE, 
                                         'HP values of survivors are displayed under their name.'),
    SkillType.HEADSHOT: SkillProperties('Headshot', SkillCategory.ZOMBIE_HUNTER, 
                                        'If you kill a zombie with a weapon, they stay dead.'),
    SkillType.SCENT_FEAR: SkillProperties('Scent Fear', SkillCategory.ZOMBIE, 
                                          'Survivors with fewer than 25 HP are shown as "wounded", and those with fewer than 13 HP are shown as "dying".'),
    SkillType.SCENT_TRAIL: SkillProperties('Scent Trail', SkillCategory.ZOMBIE, 
                                           'Zombie is able to sense the new positions of survivors it has had recent contact with.'),
    SkillType.SCENT_BLOOD: SkillProperties('Scent Blood', SkillCategory.ZOMBIE, 
                                         'HP values of survivors are displayed under their name.'),
    SkillType.SCENT_DEATH: SkillProperties('Scent Death', SkillCategory.ZOMBIE, 
                                           'When a zombie or survivor with this skill sees a pile of bodies, they can tell how many of them are in the process of revivifying.'),
    SkillType.DIGESTION: SkillProperties('Digestion', SkillCategory.ZOMBIE,
                                         'Whenever the zombie deals bite damage, it gains HP equal to the damage dealt.'),
    SkillType.INFECTIOUS_BITE: SkillProperties('Infectious Bite', SkillCategory.ZOMBIE, 
                                               'Bitten survivors become infected and lose 1HP per action until cured.'),
    SkillType.VIGOUR_MORTIS: SkillProperties('Vigour Mortis', SkillCategory.ZOMBIE, 
                                             'Zombie gets +10% to hit with all non-weapon attacks. The Corpse class starts with Vigour Mortis.'),
    SkillType.NECK_LURCH: SkillProperties('Neck Lurch', SkillCategory.ZOMBIE,
                                          ' Zombie gets an extra +10% to hit with bite attacks.'),
    SkillType.DEATH_GRIP: SkillProperties('Death Grip', SkillCategory.ZOMBIE,
                                          'Zombie gets an extra +15% to hit with hand attacks.'),
    SkillType.REND_FLESH: SkillProperties('Rend Flesh', SkillCategory.ZOMBIE,
                                          'Hand attacks deal an extra 1 damage.'),
    SkillType.TANGLING_GRASP: SkillProperties('Tangling Grasp', SkillCategory.ZOMBIE,
                                              'If the zombie hits with hands, its further attacks on that victim get +10% until it loses its grip.'),
    SkillType.FEEDING_DRAG: SkillProperties('Feeding Drag', SkillCategory.ZOMBIE,
                                            'Zombie is able to drag dying survivors (those with 12HP or less) out into the street, provided there are no barricades and the doors are still open.'),
    SkillType.MEMORIES_OF_LIFE: SkillProperties('Memories of Life', SkillCategory.ZOMBIE,
                                                'Zombie is able to open doors to buildings.'),
    SkillType.FEEDING_GROAN: SkillProperties('Feeding Groan', SkillCategory.ZOMBIE,
                                             'If faced with one or more survivors, the zombie can emit moans audible to characters (zombie or survivor) in nearby locations.'),
    SkillType.RANSACK: SkillProperties('Ransack', SkillCategory.ZOMBIE,
                                       'Zombie is able to damage the interior of abandoned buildings, making them harder to search and impossible to barricade until they are repaired.'),
    SkillType.LURCHING_GAIT: SkillProperties('Lurching Gait', SkillCategory.ZOMBIE,
                                             'Zombie can walk as fast as the living. They spend 1AP to walk from one square to another, versus needing 2 AP.'),
    SkillType.ANKLE_GRAB: SkillProperties('Ankle Grab', SkillCategory.ZOMBIE,
                                          ' Zombie only spends 1AP standing up (unless they died from a Headshot).'),
    SkillType.BRAIN_ROT: SkillProperties('Brain Rot', SkillCategory.ZOMBIE,
                                         'Zombie is harder to DNA-scan, and can only be revivified in a powered NT building using NecroNet access.'),
    SkillType.FLESH_ROT: SkillProperties('Flesh Rot', SkillCategory.ZOMBIE,
                                         'Zombie has a maximum of 60 Hit Points, and takes reduced damage from firearms.'),
}