# combat.py

from actions import ActionCommand

class Attack(ActionCommand):
        
        
        def attack(self, target):
        weapon = self.character.weapon
        if weapon:
            properties = ITEMS[weapon.type]

            
            if properties.item_function == ItemFunction.FIREARM and weapon.loaded_ammo == 0:
                return ActionResult(False, "Your firearm is out of ammo.")
            elif properties.item_function == ItemFunction.SCIENCE:
                result = self._science_attack(target, weapon)
                return result

            # Base attack success rate
            attack_chance = properties.attack

            # Apply skill bonuses
            if properties.item_function == ItemFunction.FIREARM:
                if self.character.has_skill(SkillType.BASIC_FIREARMS_TRAINING):
                    attack_chance += 25
                if weapon.type == ItemType.PISTOL:
                    if self.character.has_skill(SkillType.PISTOL_TRAINING):
                        attack_chance += 25
                    if self.character.has_skill(SkillType.ADV_PISTOL_TRAINING):
                        attack_chance += 10
                if weapon.type == ItemType.SHOTGUN:
                    if self.character.has_skill(SkillType.SHOTGUN_TRAINING):
                        attack_chance += 25
                    if self.character.has_skill(SkillType.ADV_SHOTGUN_TRAINING):
                        attack_chance += 10
            if properties.item_function == ItemFunction.MELEE:
                if self.character.has_skill(SkillType.HAND_TO_HAND):
                    attack_chance += 15
                if weapon.type == ItemType.KNIFE and self.character.has_skill(SkillType.KNIFE_COMBAT):
                        attack_chance += 15
                if weapon.type == ItemType.FIRE_AXE and self.character.has_skill(SkillType.AXE_PROFICIENCY):
                        attack_chance += 15
            
            roll = random.randint(1, 100)
            attack_success = roll <= attack_chance
            self.character.ap -= 1

            if attack_success:
                # Resolve action result
                self._deplete_weapon()
                target.take_damage(properties.damage)
                self.character.gain_xp(properties.damage)
                if target.is_dead:
                    self.character.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)


                if target.is_dead and self.character.has_skill(SkillType.HEADSHOT):
                    target.permadeath = True
                    if self.character.weapon:
                        message = f"You deal a headshot for {properties.damage} damage."
                        witness = f"{self.character.current_name} deals a headshot against {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                    else:
                        message = f"You deal a headshot for {properties.damage} damage. Your weapon breaks!"
                        witness = f"{self.character.current_name} deals a headshot against {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                else:
                    if self.character.weapon:
                        message = f"Your attack hits for {properties.damage} damage."
                        witness = f"{self.character.current_name} attacks {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                    else:
                        message = f"Your attack hits for {properties.damage} damage. Your weapon breaks!"
                        witness = f"{self.character.current_name} attacks {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)                    
            else:
                return ActionResult(False, "Your attack misses.")

        else: # If no weapon equipped, punch the enemy.
            roll = random.randint(1, 20)
            attack_success = roll >= ATTACK_DIFFICULTY

            self.character.ap -= 1

            if attack_success:
                target.take_damage(1)
                self.character.gain_xp(1)
                if target.is_dead:
                    self.character.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)

                return ActionResult(True, "You punch the enemy for 1 damage.", f"{self.character.current_name} punches {target.current_name}.")
            else:
                return ActionResult(False, "Your attack misses.")