# science.py

from data import ItemType, ResourcePath, SkillType, BLOCKS, BlockType
from items.base_classes import Item, ItemFunction


class DNAExtractor(Item):
    """A NecroTech DNA Extractor, capable of cataloguing the undead and uploading to NecroNet."""
    def __init__(self, character):
        super().__init__(character, ItemType.DNA_EXTRACTOR, "DNA Extractor", "a DNA extractor", ItemFunction.SCIENCE, ResourcePath('items/dna_extractor.png').path)  

    def use(self):
        if self.character.equipped != self:
            self.character.equip(self)
            return True, f"You equipped {self.description}."
        else:
            self.character.unequip()
            return True, f"You unequipped {self.description}."


class Syringe(Item):
    """A NecroTech Revivification Syringe, capable of reviving a zombie back to human form."""
    def __init__(self, character):
        super().__init__(character, ItemType.SYRINGE, "NecroTech Syringe", "a NecroTech revivification syringe", ItemFunction.SCIENCE, ResourcePath('items/syringe.png').path)  

    def use(self):
        if self.character.equipped != self:
            self.character.equip(self)
            return True, f"You equipped {self.description}."
        else:
            self.character.unequip()
            return True, f"You unequipped {self.description}."


class FirstAidKit(Item):
    """A first-aid kit, capable of healing wounds."""
    def __init__(self, character):
        super().__init__(character, ItemType.FIRST_AID_KIT, "First-Aid Kit", "a first-aid kit", ItemFunction.SCIENCE, ResourcePath('items/first_aid_kit.png').path)  

    def use(self):
        if self.character.equipped != self:
            self.character.equip(self)
            return True, f"You equipped {self.description}."
        else:
            self.character.unequip()
            return True, f"You unequipped {self.description}."
