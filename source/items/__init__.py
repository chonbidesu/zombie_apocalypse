# items.py

from data import ItemFunction


class Item:
    """Base class for all items."""
    def __init__(self, character, type, name, description, item_function, image_file):
        self.character = character
        self.type = type
        self.name = name
        self.description = description
        self.item_function = item_function
        self.image_file = image_file

    def use(self):
        """Default use method—only for instant-use items."""
        raise NotImplementedError("This item must be equipped before use.")
    
    def drop(self):
        """Drop the item."""
        self.character.inventory.remove(self)
        if self.character.equipped == self:
            self.character.equipped = None

    def equip(self):
        """Equipable items override this method."""
        raise NotImplementedError("This item cannot be equipped.")    
    
    def unequip(self):
        """Equipable items override this method."""
        raise NotImplementedError("This item cannot be unequipped.")        

    def _can_reload(self, equipped):
        if not equipped:
            return False, "You need to equip a firearm to reload."

        if equipped.item_function in [ItemFunction.MELEE, ItemFunction.SCIENCE]:
            return False, "You need to equip a firearm to reload."
        
        if equipped.loaded_ammo >= equipped.max_ammo:
            return False, "Your weapon is already fully loaded."    
        
        return True, ""      
    
    def get_block(self):
        x, y = self.character.location
        city = self.character.game.state.city
        block = city.block(x, y)
        return block     


class Weapon(Item):
    """Base class for all weapons."""
    def __init__(self, character, type, name, description, image_file, attack, damage, durability=None, max_ammo=None):
        super().__init__(character, type, name, description, "Weapon", image_file)
        self.attack = attack
        self.damage = damage

    def equip(self):
        """Using a weapon equips it to the character."""
        self.character.equip(self)

    def unequip(self):
        self.character.unequip(self)


class Firearm(Weapon):
    """Base class for all weapons."""
    def __init__(self, character, type, name, description, image_file, attack, damage, max_ammo):
        super().__init__(character, type, name, description, image_file, attack, damage, max_ammo, durability=None)
        self.item_function = ItemFunction.FIREARM
        self.loaded_ammo = max_ammo
        self.max_ammo = max_ammo

    def reload(self, amount):
        if amount:
            self.loaded_ammo = (min(self.loaded_ammo + amount, self.max_ammo))
        else:
            self.loaded_ammo = self.max_ammo


class Melee(Weapon):
    """Base class for all weapons."""
    def __init__(self, character, type, name, description, image_file, attack, damage, durability):
        super().__init__(character, type, name, description, image_file, attack, damage, durability, max_ammo=None)
        self.item_function = ItemFunction.MELEE
        self.durability = durability