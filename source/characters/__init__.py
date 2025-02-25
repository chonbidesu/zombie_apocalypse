# __init__.py

from dataclasses import dataclass

from core.settings import *
from items import ItemFunction
from characters.helper import CharacterHelper, ZombieWeapon, CharacterName
from ai import GoalManager


class Character:
    """Base class for Player and NPC Characters."""
    def __init__(self, game, name, occupation, x, y, is_human, inside=False):
        self.game = game
        self.name = name
        self.current_name = "John Doe"
        self.occupation = occupation
        self.location = (x, y)
        self.max_hp = MAX_HP
        self.hp = self.max_hp
        self.ap = 0
        self.xp = 0
        self.level = 0
        self.is_dead = False
        self.permadeath = False
        self.is_human = is_human
        self.inside = inside
        self.inventory = []
        self.equipped = None
        self.human_skills = set()
        self.zombie_skills = set()
        self.safehouse = None
        self.tagged = False

        self.goal_manager = GoalManager(self)

        self.helper = CharacterHelper(self)
        self.helper.update_name()    
        self.helper.add_starting_skill()
        self.helper.add_starting_items() 

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

        for skill in self.zombie_skills:
            self.helper.apply_skill_effect(skill, remove=True)
        for skill in self.human_skills:
            self.helper.apply_skill_effect(skill)    

    def gain_ap(self, ap):
        """Gain a certain amount of action points."""
        self.ap += ap

    def lose_ap(self, ap):
        """Lose a certain amount of action points."""
        self.ap -= ap        

    def gain_xp(self, xp):
        """Gain a certain amount of experience points."""
        self.xp += xp

    def gain_level(self):
        """Gain a level."""
        self.level += 1

    def status(self):
        """Returns the character's current status."""
        status = {
            "Name": self.current_name,
            "Occupation": self.occupation.name.title(),
            "HP": f"{self.hp} / {self.max_hp}",
            "XP": self.xp
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
        zombified = self.is_human
        self.is_dead = True
        self.is_human = False

        if zombified:
            self.helper.update_name()

            # Reassign passive skill effects
            for skill in self.human_skills:
                self.helper.apply_skill_effect(skill, remove=True)
            for skill in self.zombie_skills:
                self.helper.apply_skill_effect(skill)                