# item.py

class ItemHandler:
        
    @classmethod
    def equip(executor, target):
        return executor.actor.equip(target)

    @classmethod
    def unequip(executor, target):
        return executor.actor.unequip(target)

    @classmethod
    def use(executor, target):
        return executor.actor.use(target)

    @classmethod
    def drop(executor, target):     
        return executor.actor.drop(target)    