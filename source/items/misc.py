# misc.py

from data import ResourcePath, SkillType, ItemType
from items.base_classes import Item, ItemFunction
from core.settings import *


class PortableGenerator(Item):
    """A generator that can be installed in a building."""
    def __init__(self, character):
        super().__init__(character, ItemType.PORTABLE_GENERATOR, "Portable Generator", "a portable generator", ItemFunction.MISC, ResourcePath('items/portable_generator.png').path)

    def use(self):
        """Install the generator in the character's current location."""
        block = self.get_block()

        if self.character.inside:
            if block.generator_installed:
                return False, "A generator is already installed."
            else:
                block.generator_installed = True
                self.character.lose_ap(1)
                self.character.inventory.remove(self)
                return True, "You install a generator. It needs fuel to operate."
            
        else:
            return False, "Generators need to be installed inside buildings."     


class FuelCan(Item):
    """A fuel can that can be used to fuel generators to power buildings."""
    def __init__(self, character):
        super().__init__(character, ItemType.FUEL_CAN, "Fuel Can", "a fuel can", ItemFunction.MISC, ResourcePath('items/fuel_can.png').path)   

    def use(self):
        """Fuel the generator installed in the current building."""
        block = self.get_block()

        if self.character.inside:

            if block.lights_on:
                return False, "Generator already has fuel."
            elif not block.generator_installed:
                return False, "You need to install a generator first."
            else:
                self.character.lose_ap(1)
                block.fuel_expiration = self.character.game.ticker + FUEL_DURATION
                block.lights_on = True
                self.character.inventory.remove(self)
                return True, "You fuel the generator. The lights are now on."

        else:
            return False, "You have to be inside a building to use this."        
        

class Toolbox(Item):
    """A toolbox that can be used to repair buildings."""
    def __init__(self, character):
        super().__init__(character, ItemType.TOOLBOX, "Toolbox", "a toolbox", ItemFunction.MISC, ResourcePath('items/toolbox.png').path)  

    def use(self):
        block = self.get_block()

        if self.character.inside:

            if block.ransack_level == 0:
                return False, "This building does not need repairs."

            if block.ruined:
                if not block.lights_on:
                    return False, "Ruined buildings need to be powered in order to be repaired."
                elif not SkillType.CONSTRUCTION in self.character.human_skills:
                    return False, "You need the Construction skill to repair ruins."
                else:
                    self.character.lose_ap(1)
                    block.repair()        
                    return True, "You repair the damage to the building, clearing the rubble and cleaning up the mess."
            else:
                self.character.lose_ap(1)
                block.repair()        
                return True, "You repaired the interior of the building and cleaned up the mess."
        else:
            return False, "You have to be inside a building to use this."        
        

class FirstAidKit(Item):
    """A first-aid kit, capable of healing wounds."""
    def __init__(self, character):
        super().__init__(character, ItemType.FIRST_AID_KIT, "First-Aid Kit", "a first-aid kit", ItemFunction.MISC, ResourcePath('items/first_aid_kit.png').path)  

    def use(self):
        if self.character.equipped != self:
            self.character.equip(self)
            return True, f"You equipped {self.description}."
        else:
            self.character.unequip()
            return True, f"You unequipped {self.description}."
        

class Consumable(Item):
    """A consumable item (beer, wine, or candy) that provides a minor health boost."""
    def __init__(self, character, type):
        super().__init__(character, type, "", "", ItemFunction.MISC, ResourcePath(f'items/{type.name.lower()}.png').path)  
        self.set_description()

    def use(self):
        self.character.inventory.remove(self)
        self.character.heal(1)
        self.character.lose_ap(1)
        return True, f"You consume {self.description}."      
    
    def set_description(self):
        if self.type == ItemType.BEER:
            self.name = 'Beer'
            self.description = 'a can of beer'
        elif self.type == ItemType.WINE:
            self.name = 'Wine'
            self.description = 'a bottle of wine'
        elif self.type == ItemType.CANDY:
            self.name = 'Stale Candy'
            self.description = 'a stale piece of candy'        


class Map(Item):
    """A map of the City of Malton."""
    def __init__(self, character):
        super().__init__(character, ItemType.MAP, "Map", "a City of Malton map", ItemFunction.MISC, ResourcePath('items/map.png').path)  

    def use(self):
        self.character.game.reading_map = True
        return True, "You open the map."

class Binoculars(Item):
    """A pair of binoculars."""
    def __init__(self, character):
        super().__init__(character, ItemType.BINOCULARS, "Binoculars", "a pair of binoculars", ItemFunction.MISC, ResourcePath('items/binoculars.png').path)  

    def use(self):
        return True, "You use the binoculars."


class Book(Item):
    """A book of some kind."""
    def __init__(self, character):
        super().__init__(character, ItemType.BOOK, "Book", "a book", ItemFunction.MISC, ResourcePath('items/book.png').path)

    def use(self):
        return True, "You read the book."          

class PoetryBook(Item):
    """A book of poetry."""
    def __init__(self, character):
        super().__init__(character, ItemType.POETRY_BOOK, "Book of Poetry", "a book of poetry", ItemFunction.MISC, ResourcePath('items/poetry_book.png').path)

    def use(self):
        return True, "You read the book of poetry."       

class Crucifix(Item):
    """A wooden cross with a figure of Jesus in suffering."""
    def __init__(self, character):
        super().__init__(character, ItemType.CRUCIFIX, "Crucifix", "a crucifix", ItemFunction.MISC, ResourcePath('items/crucifix.png').path)

    def use(self):
        return True, "You hold the crucifix in front of you, in hopes it offers some protection."    

class GPSUnit(Item):
    """A GPS unit, showing the character's coordinates."""
    def __init__(self, character):
        super().__init__(character, ItemType.GPS_UNIT, "GPS Unit", "a GPS unit", ItemFunction.MISC, ResourcePath('items/gps_unit.png').path)

    def use(self):
        return True, "You use the GPS unit."   

class Newspaper(Item):
    """A daily newspaper."""
    def __init__(self, character):
        super().__init__(character, ItemType.NEWSPAPER, "Newspaper", "a daily newspaper", ItemFunction.MISC, ResourcePath('items/newspaper.png').path)

    def use(self):
        return True, "You read the newspaper."