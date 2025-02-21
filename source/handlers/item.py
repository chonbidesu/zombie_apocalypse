# item.py

class ItemHandler:
        
    @staticmethod
    def equip(executor, item):
        return executor.actor.state.equip(item)

    @staticmethod
    def unequip(executor, item):
        return executor.actor.state.unequip(item)

    @staticmethod
    def use(executor, item):
        return executor.actor.state.use(item)

    @staticmethod
    def drop(executor, item):     
        return executor.actor.state.drop(item)    