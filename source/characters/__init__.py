# __init__.py

from dataclasses import dataclass

from core.settings import *
from items import ItemFunction
from .helper import CharacterHelper, ZombieWeapon, CharacterName
from .skill_manager import SkillManager
from ai import GoalManager
from data import SkillType


class Character:
    """Base class for Player and NPC Characters."""
    def __init__(self, game, name, occupation, x, y, is_human, inside=False):
        self.game = game
        self.name = name
        self.occupation = occupation
        self.location = (x, y)
        self.is_human = is_human
        self.ap = 0
        self.xp = 0
        self.level = 0
        self.is_dead = False
        self.time_of_death = 0
        self.permadeath = False
        self.inside = inside
        self.inventory = []
        self.equipped = None
        self.human_skills = set()
        self.zombie_skills = set()
        self.safehouse = None
        self.tagged = False

        self.goal_manager = GoalManager(self)
        self.skill_manager = SkillManager(self)

        self.helper = CharacterHelper(self)
        self.helper.add_starting_skill()
        self.helper.add_starting_items()

        self.hp = self.max_hp

    @property
    def max_hp(self):
        """Returns the character's maximum health points."""
        base_hp = MAX_HP
        if self.is_human and self.helper.has_skill(SkillType.BODY_BUILDING):
            base_hp += 10
        if not self.is_human and self.helper.has_skill(SkillType.FLESH_ROT):
            base_hp += 10
        return base_hp        

    @property
    def current_name(self):
        """Returns the character's name based on their current state."""
        if self.is_human:
            return f"{self.name.first_name} {self.name.last_name}"
        else:
            return f"{self.name.zombie_adjective} {self.name.first_name}"

    def take_damage(self, amount, fatal=True):
        """Reduces the character's health by the given amount."""
        self.hp -= amount
        if self.hp <= 0:
            if fatal:
                self.hp = 0
                self.die()
            else:
                self.hp = 1
        elif self == self.game.state.player:  # Trigger red flicker effect for the player only
            self.game.game_ui.screen_transition.flicker_red()                

    def heal(self, amount):
        """Heals the character by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def revive(self):
        """Revives the character to human state."""
        self.is_dead = True
        self.is_human = True   

    def gain_ap(self, ap):
        """Gain a certain amount of action points."""
        self.ap += ap

    def lose_ap(self, ap):
        """Lose a certain amount of action points."""
        self.ap -= ap        

    def gain_xp(self, xp):
        """Gain a certain amount of experience points."""
        self.xp += xp

    def lose_xp(self, xp):
        """Lose a certain amount of experience points."""
        self.xp -= xp

    def gain_level(self):
        """Gain a level."""
        self.level += 1

    def status(self):
        """Returns the character's current status."""
        status = {
            "Name": self.current_name,
            "Occupation": self.occupation.name.title(),
            "HP": f"{self.hp} / {self.max_hp}",
            "XP": self.xp,
            "Location": self.location,
        }
        return status
    
    def equip(self, item):
        self.equipped = item

    def unequip(self):
        self.equipped = None   

    def drop(self, item):
        self.inventory.remove(item)
        if item == self.equipped:
            self.equipped = None

    def deplete_weapon(self):
        """Reduce loaded ammo or durability, depending on weapon type."""
        if self.equipped.item_function == ItemFunction.FIREARM:
            self.equipped.loaded_ammo -= 1
        elif self.equipped.item_function == ItemFunction.MELEE:
            self.equipped.durability -= 1
            if self.equipped.durability <= 0:
                self.inventory.remove(self.equipped)
                self.equipped = None  

    def enter(self):
        self.inside = True

    def leave(self):
        self.inside = False

    def move(self, x, y):
        self.location = (x, y)

    def fall(self):
        """Character falls from a building, taking damage."""
        self.take_damage(5, fatal=False)
        if self == self.game.state.player:
            self.game.chat_history.append("You fall from the crumbling building, injuring yourself.")             

    def stand(self):
        self.is_dead = False

    def die(self):
        """Handles the character's death."""
        self.is_dead = True
        self.is_human = False
        self.time_of_death = self.game.ticker              