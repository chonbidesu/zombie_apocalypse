# __init__.py

from dataclasses import dataclass
import random

from settings import *
from data import ITEMS, ItemType, ItemFunction, SKILLS, SkillType, SkillCategory, OCCUPATIONS, BLOCKS, ActionResult
from characters.items import Item, Weapon
from characters.human_state import Human
from characters.zombie_state import Zombie
from characters.actions import ActionExecutor


@dataclass
class CharacterName:
    first_name: str
    last_name: str
    zombie_adjective: str


class Character:
    """Base class for Player and NPC Characters."""
    def __init__(self, game, name, occupation, x, y, is_human, inside=False):
        self.game = game
        self.name = name
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
        self.weapon = None
        self.state = self.get_state()
        self.human_skills = set()
        self.zombie_skills = set()
        self.action = ActionExecutor(game, self)

        self.add_starting_skill()
        self.add_starting_items()

    def update_name(self):
        """Updates the character's name based on their current state."""
        if self.is_human:
            self.current_name = f"{self.name.first_name} {self.name.last_name}"
        else:
            self.current_name = f"{self.name.zombie_adjective} {self.name.first_name}"

    def get_state(self):
        """Set state based on is_human."""
        if self.is_human:
            state = Human(self.game, self)
            self.update_name()
        else:
            state = Zombie(self.game, self)
            self.update_name()
        return state

    def add_starting_skill(self):
        """Adds a starting skill depending on player's occupation."""
        occupation_properties = OCCUPATIONS[self.occupation]
        starting_skill = occupation_properties.starting_skill
        self.add_skill(starting_skill)

    def add_starting_items(self):
        """Adds starting items depending on player's occupation."""
        occupation_properties = OCCUPATIONS[self.occupation]
        starting_items = occupation_properties.starting_items
        for item_type in starting_items:
            item = self.create_item(item_type)
            self.inventory.append(item)

    def add_skill(self, skill):
        """Add a skill to the character's skill set."""
        if skill in SKILLS:
            skill_category = SKILLS[skill].skill_category

            if skill_category == SkillCategory.ZOMBIE:
                self.zombie_skills.add(skill)
            else:
                self.human_skills.add(skill)

            self.apply_skill_effect(skill)
            self.level += 1

    def has_skill(self, skill):
        """Check if a character has a particular skill."""
        return skill in self.human_skills or skill in self.zombie_skills

    def apply_skill_effect(self, skill, remove=False):
        """Apply or remove the passive effects of a skill."""
        if remove:
            modifier = -1
        else:
            modifier = 1

        if skill == SkillType.BODY_BUILDING:
            self.max_hp += 10 * modifier
        elif skill == SkillType.FLESH_ROT:
            self.max_hp += 10 * modifier

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

    def fall(self):
        """Character falls from a building, taking damage."""
        self.take_damage(5, fatal=False)
        if self == self.game.state.player:
            self.game.chat_history.append("You fall from the crumbling building, injuring yourself.")

    def heal(self, amount):
        """Heals the character by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def die(self):
        """Handles the character's death."""
        if self.is_human:
            zombified = True
        else:
            zombified = False

        self.is_dead = True
        self.is_human = False
        self.state = Zombie(self.game, self)
        self.update_name()

        # Reassign passive skill effects
        if zombified:
            for skill in self.human_skills:
                self.apply_skill_effect(skill, remove=True)
            for skill in self.zombie_skills:
                self.apply_skill_effect(skill)

    def revivify(self):
        """Revives the character to human state."""
        self.is_dead = True
        self.is_human = True
        self.state = Human(self.game, self)
        self.update_name()
        for skill in self.zombie_skills:
            self.apply_skill_effect(skill, remove=True)
        for skill in self.human_skills:
            self.apply_skill_effect(skill)    

    def gain_xp(self, xp):
        """Gain a certain amount of experience points."""
        self.xp += xp

    def status(self):
        """Returns the character's current status."""
        status = {
            "Name": self.current_name,
            "Occupation": self.occupation.name.title(),
            "HP": f"{self.hp} / {self.max_hp}",
            "XP": self.xp
        }
        return status
    
    def create_item(self, type):
        """Create an item based on its type."""
        # Check if the item is a weapon
        item_type = getattr(ItemType, type)
        properties = ITEMS[item_type]
        if properties.item_function == ItemFunction.MELEE:
            # Create a melee weapon
            weapon = Weapon(type=item_type)
            return weapon
        elif properties.item_function == ItemFunction.FIREARM:
            # Create a firearm
            weapon = Weapon(type=item_type)
            return weapon
        elif properties.item_function in [ItemFunction.ITEM, ItemFunction.AMMO, ItemFunction.SCIENCE]:
            # Create a regular item
            item = Item(type=item_type)
            return item
        
    def stand(self):
        """Character stands up at full health."""
        if not self.permadeath:
            self.is_dead = False
            self.hp = self.max_hp // 2
            if SkillType.ANKLE_GRAB in self.zombie_skills:
                self.ap -= 1
            else:
                self.ap -= STAND_AP    

    def enter(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building:
            if not self.inside:
                if self.is_human:
                    if building.barricade.level == 0:
                        self.inside = True
                        self.ap -= 1
                        message = "You entered the building."
                        witness = f"{self.current_name} entered the building."
                        return ActionResult(True, message, witness, sfx='footsteps')
                    elif building.barricade.level <= 4:
                        self.inside = True
                        self.ap -= 1
                        message = "You climb through the barricades and are now inside."
                        witness = f"{self.current_name} climbed through the barricades and is now inside."
                        return ActionResult(True, message, witness, sfx='footsteps')
                    else:
                        return ActionResult(False, "You can't find a way through the barricades.")
                else:
                    if building.barricade.level == 0:
                        if building.doors_closed:
                            if SkillType.MEMORIES_OF_LIFE in self.zombie_skills:
                                building.doors_closed = False
                                self.inside = True
                                self.ap -= 1
                                message = "You enter the building, leaving the doors wide open."
                                witness = f"{self.current_name} entered the building, leaving the doors wide open."
                                return ActionResult(True, message, witness, sfx='footsteps')
                            else:
                                return ActionResult(False, "You need the MEMORIES OF LIFE skill in order to open doors.")
                        else:
                            self.inside = True
                            self.ap -= 1
                            message = "You enter the building."
                            witness = f"{self.current_name} entered the building."
                            return ActionResult(True, message, witness, sfx='footsteps')   
                    else:
                        return ActionResult(False, "You have to break through the barricades first.")
            else:
                return ActionResult(False, "You are already inside.")
        else:
            return ActionResult(False, "This is not a building.")

    def leave(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building and self.inside:
            if self.is_human:
                if building.barricade.level == 0:
                    self.inside = False
                    self.ap -= 1
                    message = "You left the building."
                    witness = f"{self.current_name} left the building."
                    return ActionResult(True, message, witness, sfx='footsteps')
                if building.barricade.level <= 4:
                    self.inside = False
                    self.ap -= 1
                    message = "You climb through the barricades and are now outside."
                    witness = f"{self.current_name} climbed through the barricades and is now outside."
                    return ActionResult(True, message, witness, sfx='footsteps')
                else:
                    return ActionResult(False, "The building has been so heavily barricaded that you cannot leave through the main doors.")
            else:
                if building.barricade.level == 0:
                    if building.doors_closed:
                        if SkillType.MEMORIES_OF_LIFE in self.zombie_skills:
                            self.inside = False
                            self.ap -= 1
                            message = "You left the building, leaving the doors wide open."
                            witness = f"{self.current_name} left the building, leaving the doors wide open."
                            return ActionResult(True, message, witness, sfx='footsteps')   
                        else:
                            return ActionResult(False, "You need the MEMORIES OF LIFE skill in order to open doors.")                         
                    else:
                        self.inside = False
                        self.ap -= 1
                        message = "You left the building."
                        witness = f"{self.current_name} left the building."
                        return ActionResult(True, message, witness, sfx='footsteps')
                else:
                    return ActionResult(False, "You have to break through the barricades first.")
        else:
            return ActionResult(False, "You can't leave this place.")

    def move(self, dx, dy):
        """Moves the character to a new location."""
        city = self.game.state.city
        x, y = self.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:
            new_block = city.block(new_x, new_y)
            block_properties = BLOCKS[new_block.type]
            is_human = self.is_human

            # If a player moves, they are no longer inside unless they have Free Running.
            if is_human:
                if block_properties.is_building:
                    if SkillType.FREE_RUNNING not in self.human_skills:
                        self.inside = False
                    else:
                        if new_block.ruined:
                            self.inside = False
                            self.fall()
                else:
                    self.inside = False
                self.ap -= 1
            else:
                self.inside = False
                if SkillType.LURCHING_GAIT in self.zombie_skills:
                    self.ap -= 1
                else:
                    self.ap -= 2
            self.location = (new_x, new_y)
        
        else:
            return False

    def wander(self):
        """Randomly moves the actor to an adjacent block."""
        x, y = self.location[0], self.location[1]
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        new_x, new_y = x + dx, y + dy
        is_human = self.is_human

        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:  # Ensure within city bounds
            if is_human:
                self.ap -= 1
            else:
                self.ap -= 2
            self.location = (new_x, new_y)
            self.inside = False
            return ActionResult(True)
        return ActionResult(False)

    def _deplete_weapon(self):
        """Reduce loaded ammo or durability, depending on weapon type."""
        properties = ITEMS[self.weapon.type]
        if properties.item_function == ItemFunction.FIREARM:
            self.weapon.loaded_ammo -= 1
        elif properties.item_function == ItemFunction.MELEE:
            self.weapon.durability -= 1
            if self.weapon.durability <= 0:
                self.inventory.remove(self.weapon)
                self.weapon = None        

    def reload(self):
        if not self.weapon:
            return ActionResult(False, "You need to equip a firearm to reload.")

        properties = ITEMS[self.weapon.type]
        if properties.item_function == ItemFunction.MELEE:
            return ActionResult(False, "You need to equip a firearm to reload.")

        if self.weapon.type == ItemType.PISTOL:
            self.ap -= 1
            return ActionResult(True, "You slap a new pistol clip into your gun.")
        elif self.weapon.type == ItemType.SHOTGUN:
            self.ap -= 1
            return ActionResult(True, "You load a shell into your shotgun.")
 
    def equip(self, item):        
        properties = ITEMS[item.type]
        self.weapon = item
        return ActionResult(True, f"You equip {properties.description}.")

    def unequip(self, item):
        properties = ITEMS[item.type]
        self.weapon = None
        return ActionResult(True, f"You unequip {properties.description}.")

    def use(self, item):
        x, y = self.location
        block = self.game.state.city.block(x, y)
        usage = {
            ItemType.PORTABLE_GENERATOR: block.install_generator,
            ItemType.FUEL_CAN: block.fuel_generator,
            ItemType.TOOLBOX: block.repair_building,
            ItemType.BEER: self.consume_item,
            ItemType.WINE: self.consume_item,
            ItemType.CANDY: self.consume_item,
            ItemType.CRUCIFIX: self.help_me_jesus,
            ItemType.MAP: self.read_map,
            ItemType.PISTOL_CLIP: self.reload,
            ItemType.SHOTGUN_SHELL: self.reload,
        }
  
        if item.type in usage:  
            return usage[item.type](item)      
          
            result = block.install_generator()
            if result.success:
                self.ap -= 1
                self.actor.inventory.remove(item)
            return result
    
        elif item.type == ItemType.FUEL_CAN:
            result = self.fuel_generator(block)
            if result.success:
                self.actor.ap -= 1
                block.fuel_expiration = self.game.ticker + FUEL_DURATION
                block.lights_on = True
                self.actor.inventory.remove(item)
            return result

        elif item.type == ItemType.TOOLBOX:
            result = self.repair_building(block)
            if result.success:
                self.actor.ap -= 1
                block.ransack_level = 0
                block.ruined = False
            return result
        
        elif item.type in [
            ItemType.BEER, ItemType.WINE, ItemType.CANDY
        ]:
            result = self.consume_item(item)
            if result.success:
                self.actor.ap -= 1
            return result

        elif item.type == ItemType.CRUCIFIX:
            return ActionResult(True, "You hold the crucifix out in front of you, hoping it will offer some protection.")

        elif item.type == ItemType.MAP:
            self.game.reading_map = True
        
        elif item.type == ItemType.PISTOL_CLIP:
            result = self.reload(weapon)
            if result.success:
                self.actor.ap -= 1
                weapon.loaded_ammo = weapon.max_ammo
                self.actor.inventory.remove(item)
            return result

        elif item.type == ItemType.SHOTGUN_SHELL:
            result = self.reload(weapon)
            if result.success:       
                self.actor.ap -= 1
                weapon.loaded_ammo += 1                
                self.actor.inventory.remove(item)          
            return result

    def drop(self, item):
        properties = ITEMS[item.type]
        self.actor.inventory.remove(item)
        return ActionResult(True, f"You drop {properties.description}.")

    def consume_item(self, item):
        properties = ITEMS[item.type]
        self.actor.inventory.remove(item)
        self.actor.heal(1)
        return ActionResult(True, f"You consume {properties.description}.")

    def heal(self, target, item):
        player = self.game.state.player
        x, y = self.actor.location
        block = self.game.state.city.block(x, y)

        block_properties = BLOCKS[block.type]
        if SkillType.FIRST_AID in self.actor.human_skills:
            heal_bonus = 5
            if SkillType.SURGERY in self.actor.human_skills and block_properties.type == BlockType.HOSPITAL and block.lights_on:
                heal_bonus += 5
        else:
            heal_bonus = 0
        if target.hp < target.max_hp:
            target.heal(5 + heal_bonus)
            self.actor.inventory.remove(item)
            self.actor.weapon = None
            self.actor.ap -= 1
            if target == self.actor:
                return ActionResult(True, "You use a first aid kit on yourself, and feel a bit better.")
            else:
                return ActionResult(True, f"You use a first aid kit on {target.current_name}, and they gain some health.")
        else:
            if target == self.actor:
                return ActionResult(False, "You already feel healthy.")
            else:
                return ActionResult(False, f"{target.current_name} already feels healthy.") 

    