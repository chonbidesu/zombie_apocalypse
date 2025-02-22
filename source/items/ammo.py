# ammo.py

from data import ResourcePath, ItemType, ItemFunction
from items import Item


class ShotgunShell(Item):
    """A red ammunition shell for a shotgun."""
    def __init__(self, character):
        super().__init__(character, ItemType.SHOTGUN_SHELL, "Shotgun Shell", "a shotgun shell", ItemFunction.AMMO, ResourcePath('items/shotgun_shell.png').path)

    def use(self):
        equipped = self.character.equipped

        can_reload, message = self._can_reload(equipped)

        if can_reload:
            equipped.reload(1)
            self.character.lose_ap(1)
            self.character.inventory.remove(self)
            return True, "You load a shell into your shotgun."    
        else:
            return False, message



class PistolClip(Item):
    """An ammunition magazine for a pistol."""
    def __init__(self, character):
        super().__init__(character, ItemType.PISTOL_CLIP, "Pistol Clip", "a pistol clip", ItemFunction.AMMO, ResourcePath('items/pistol_clip.png').path)       

    def use(self):
        equipped = self.character.equipped

        can_reload, message = self._can_reload(equipped)

        if can_reload:
            equipped.reload(0)   
            self.character.lose_ap(1)
            self.character.inventory.remove(self)
            return True, "You slap a new pistol clip into your gun."
        
        else:
            return False, message