# state.py

from dataclasses import dataclass
import random

from data import Action, ActionResult, SKILLS, SkillType, SkillCategory, OCCUPATIONS, OccupationCategory, ITEMS, ItemType, ItemFunction, BLOCKS, BlockType
from settings import *


@dataclass
class MoveTarget:
    dx: int = 0
    dy: int = 0


@dataclass
class BehaviourResult:
    action: Action
    target: object = None


@dataclass
class BlockNPCs:
    x: int
    y: int
    inside: bool
    living_humans: list
    living_zombies: list
    dead_bodies: list
    dead_zombies: list
    revivifying_bodies: list


class State:
    """Represents an NPC state."""
    def __init__(self, character):
        self.game = character.game
        self.character = character # Reference the parent character
        self.current_target = None
        self.next_action = None
        self.selected_skill = None

    def get_action(self):
        """Determines next behaviour and stores the action."""
        self.next_action = self._determine_behaviour()

    def act(self):
        """Execute AI behaviour."""
        # Only act if action points are available
        if self.character.ap < 1:
            return False

        # Execute action if one was determined
        if self.next_action:
            action_result = self.character.action.execute(self.next_action.action, self.next_action.target)
            if action_result:
                if action_result.attacked and self.next_action.target == self.game.state.player:
                    self.game.chat_history.append(action_result.attacked)
                elif action_result.witness and self.character.location == self.game.state.player.location:
                    if self.character.inside == self.game.state.player.inside:
                        self.game.chat_history.append(action_result.witness) 
                        if action_result.sfx:
                            pygame.mixer.Sound.play(self.game.sounds[action_result.sfx])                        
                    else:
                        if self.next_action.action == Action.DECADE or self.next_action.action == Action.ENTER:
                            self.game.chat_history.append(action_result.witness)
                            if action_result.sfx:
                                pygame.mixer.Sound.play(self.game.sounds[action_result.sfx])                               

    def filter_characters_at_location(self, x, y, inside=False, include_player=True):
        """Retrieve all characters at a given location and categorize them."""
        player = self.game.state.player
        characters_here = [
            npc for npc in self.game.state.npcs.list
            if npc.location == (x, y) and npc.inside == inside
        ]

        if include_player:
            # Add the player to the list if they are at location
            if player.location == (x, y) and player.inside == inside:
                characters_here.append(player)

        zombies_here = [character for character in characters_here if not character.is_human]
        humans_here = [character for character in characters_here if character.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [c for c in characters_here if c.is_dead]
        dead_zombies = [z for z in zombies_here if z.is_dead]
        revivifying_bodies = [h for h in humans_here if h.is_dead]

        return BlockNPCs(x, y, inside, living_humans, living_zombies, dead_bodies, dead_zombies, revivifying_bodies)                      
    
    def get_adjacent_locations(self):
        """Returns a list of (x, y) coordinates for the 8 adjacent blocks."""
        x, y = self.character.location
        adjacent_locations = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), # Top row
            (x - 1, y),                 (x + 1, y),     # Middle row
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)  # Bottom row
        ]
        valid_locations = []

        # Filter only valid locations in bounds
        for location in adjacent_locations:
            x, y = location
            if 0 < x < CITY_SIZE - 1 and 0 < y < CITY_SIZE - 1:
                valid_locations.append(location)
        return valid_locations
    
    def _make_choice(self, actions):
        """Choose an action based on weighted probabilities."""
        valid_actions = [(action, weight) for action, weight in actions.items() if weight > 0]
        if not valid_actions:
            return None # No valid actions
        
        choices, weights = zip(*valid_actions)
        return random.choices(choices, weights=weights, k=1)[0] # Select an action    
    
    def gain_skill(self):
        """If enough XP available, gain a skill."""
        if self.character.is_dead:
            return
        
        if not self.selected_skill:
            self.selected_skill = self.select_skill()

        if self.selected_skill:
            skill_xp_cost = self._get_skill_xp_cost(self.selected_skill)

            if self.character.xp >= skill_xp_cost:
                self.character.add_skill(self.selected_skill)

                self.character.xp -= skill_xp_cost
                self.selected_skill = None

    def select_skill(self):
        """Selects a skill to learn."""
        occupation_category = OCCUPATIONS[self.character.occupation].occupation_category

        if self.character.is_human:
            skills = [
                skill for skill, properties in SKILLS.items() 
                if properties.skill_category != SkillCategory.ZOMBIE and
                (properties.skill_category != SkillCategory.ZOMBIE_HUNTER or self.character.level >= 10)
            ]
        else:
            skills = [skill for skill, properties in SKILLS.items() 
                      if properties.skill_category == SkillCategory.ZOMBIE]           

        acquired_skills = set(self.character.human_skills) if self.character.is_human else set(self.character.zombie_skills)

        # Filter skills where prerequisites are met
        skills_with_prereqs_met = [
            skill for skill in skills 
            if all(prerequisite in acquired_skills for prerequisite in SKILLS[skill].prerequisite_skills)
        ]

        occupation_skills = [skill for skill, properties in SKILLS.items() if skill in skills_with_prereqs_met and properties.skill_category == occupation_category]

        # Prioritize occupational skills
        if occupation_skills:
                return random.choice(occupation_skills) if random.random() < 0.75 else random.choice(skills_with_prereqs_met)
                
        # If no occupation skills are available, pick any valid skill
        if skills_with_prereqs_met:
            return random.choice(skills_with_prereqs_met)
            
        return None

    def _get_skill_xp_cost(self, skill):
        """Calculate the XP cost for the given skill based on the player's occupation."""
        player = self.game.state.player
        skill_category = SKILLS[skill].skill_category
        occupation_category = OCCUPATIONS[player.occupation].occupation_category

        if skill_category == SkillCategory.CIVILIAN:
            return 100 # Fixed cost for civilian skills
        
        elif skill_category == SkillCategory.MILITARY:
            if occupation_category == OccupationCategory.MILITARY:
                return 75
            elif occupation_category == OccupationCategory.CIVILIAN:
                return 100
            else: # Science occupation
                return 150
            
        elif skill_category == SkillCategory.SCIENCE:
            if occupation_category == OccupationCategory.SCIENCE:
                return 75
            elif occupation_category == OccupationCategory.CIVILIAN:
                return 100
            else: # Military occupation
                return 150
            
        elif skill_category == SkillCategory.ZOMBIE_HUNTER:
            return 100
            
        elif skill_category == SkillCategory.ZOMBIE:
            return 100 # Fixed cost for zombie skills     

    def stand(self):
        """Character stands up at full health."""
        if not self.character.permadeath:
            self.character.is_dead = False
            self.character.hp = self.character.max_hp // 2
            if self.character.has_skill(SkillType.ANKLE_GRAB):
                self.character.ap -= 1
            else:
                self.character.ap -= STAND_AP             

    def reload(self, actor, item):
        if not actor.weapon:
            return ActionResult(False, "You need to equip a firearm to reload.")

        properties = ITEMS[actor.weapon.type]
        if properties.item_function == ItemFunction.MELEE:
            return ActionResult(False, "You need to equip a firearm to reload.")
        
        if actor.weapon.loaded_ammo >= actor.weapon.max_ammo:
            return ActionResult(False, "Your weapon is already fully loaded.")

        if actor.weapon.type == ItemType.PISTOL:
            actor.weapon.loaded_ammo = actor.weapon.max_ammo   
            message = "You slap a new pistol clip into your gun."
        elif actor.weapon.type == ItemType.SHOTGUN:
            actor.weapon.loaded_ammo += 1
            message = "You load a shell into your shotgun."
        actor.ap -= 1
        actor.inventory.remove(item)
        return ActionResult(True, message)
 
    def equip(self, item):        
        properties = ITEMS[item.type]
        self.character.weapon = item
        return ActionResult(True, f"You equip {properties.description}.")

    def unequip(self, item):
        properties = ITEMS[item.type]
        self.character.weapon = None
        return ActionResult(True, f"You unequip {properties.description}.")

    def use(self, item):
        x, y = self.character.location
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
            return usage[item.type](self.character, item)      
          
    def drop(self, item):
        properties = ITEMS[item.type]
        self.character.inventory.remove(item)
        return ActionResult(True, f"You drop {properties.description}.")

    def consume_item(self, actor, item):
        properties = ITEMS[item.type]
        self.character.inventory.remove(item)
        self.character.heal(1)
        self.character.ap -= 1
        return ActionResult(True, f"You consume {properties.description}.")

    def help_me_jesus(self, actor, item):
        return ActionResult(True, "You hold the crucifix out in front of you, hoping it will offer some protection.")

    def read_map(self, actor, item):
        self.game.reading_map = True

    def heal(self, target):
        x, y = self.character.location
        block = self.game.state.city.block(x, y)

        block_properties = BLOCKS[block.type]
        if self.character.has_skill(SkillType.FIRST_AID):
            heal_bonus = 5
            if self.character.has_skill(SkillType.SURGERY) and block_properties.type == BlockType.HOSPITAL and block.lights_on:
                heal_bonus += 5
        else:
            heal_bonus = 0
        if target.hp < target.max_hp:
            target.heal(5 + heal_bonus)
            self.character.inventory.remove(self.character.weapon)
            self.character.weapon = None
            self.character.ap -= 1
            if target == self.character:
                return ActionResult(True, "You use a first aid kit on yourself, and feel a bit better.")
            else:
                return ActionResult(True, f"You use a first aid kit on {target.current_name}, and they gain some health.")
        else:
            if target == self.character:
                return ActionResult(False, "You already feel healthy.")
            else:
                return ActionResult(False, f"{target.current_name} already feels healthy.") 
            
    def inject(self, target):
        if target.is_human:
            return ActionResult(False, "You cannot inject humans.")
        else:
            x, y = self.character.location
            city = self.game.state.city
            block = city.block(x, y)

            if self.character.inside:
                if block.lights_on:
                    return self._inject_success(target)
                else:
                    success = random.randint(0, 1) == 1
                    if success:
                        return self._inject_success(target)
                    else:
                        return ActionResult(False, "While priming the needle, you happen to lose track of the zombie in the dark.")
            else:
                return self._inject_success(target)

    def _inject_success(self, target):
        target.revivify()
        self.character.ap -= 10

        # Trigger NPC sprite animation if visible
        sprites = list(self.game.game_ui.description_panel.human_sprite_group)
        for sprite in sprites:
            if target == sprite.npc:
                sprite.set_action(2)

        return ActionResult(True, "Following standard procedures, you press the syringe into the back of the zombie's neck and pump the glittering serum into its brain and spinal cord.")

