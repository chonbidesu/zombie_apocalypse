# science.py

from data import ItemType, ItemFunction, ResourcePath, SkillType, BLOCKS, BlockType
from items import Item


class DNAExtractor(Item):
    """A NecroTech DNA Extractor, capable of cataloguing the undead and uploading to NecroNet."""
    def __init__(self, character):
        super().__init__(character, ItemType.DNA_EXTRACTOR, "DNA Extractor", "a DNA extractor", ItemFunction.SCIENCE, ResourcePath('items/dna_extractor.png').path)  

    def equip(self):
        """Equip the DNA extractor."""
        self.character.equip(self) 


class Syringe(Item):
    """A NecroTech Revivification Syringe, capable of reviving a zombie back to human form."""
    def __init__(self, character):
        super().__init__(character, ItemType.SYRINGE, "NecroTech Syringe", "a NecroTech revivification syringe", ItemFunction.SCIENCE, ResourcePath('items/syringe.png').path)  

    def equip(self):
        """Equip the revivification syringe."""
        self.character.equip(self)  


class FirstAidKit(Item):
    """A first-aid kit, capable of healing wounds."""
    def __init__(self, character):
        super().__init__(character, ItemType.FIRST_AID_KIT, "First-Aid Kit", "a first-aid kit", ItemFunction.SCIENCE, ResourcePath('items/first_aid_kit.png').path)  

    def equip(self):
        """Equip the first-aid kit."""
        self.character.equip(self)

    def use(self, target):
        x, y = self.character.location
        city = self.character.game.state.city
        block = city.block(x, y)

        block_properties = BLOCKS[block.type]
        if self.character.has_skill(SkillType.FIRST_AID):
            heal_bonus = 5
            if self.character.has_skill(SkillType.SURGERY) and block_properties.type == BlockType.HOSPITAL and block.lights_on:
                heal_bonus += 5
        else:
            heal_bonus = 0
        if target.hp < target.max_hp:
            target.heal(5 + heal_bonus)
            self.character.inventory.remove(self)
            self.character.equipped = None
            self.character.lose_ap(1)
            if target == self.character:
                return True, "You use a first aid kit on yourself, and feel a bit better."
            else:
                return True, f"You use a first aid kit on {target.current_name}, and they gain some health."
        else:
            if target == self.character:
                return False, "You already feel healthy."
            else:
                return False, f"{target.current_name} already feels healthy."