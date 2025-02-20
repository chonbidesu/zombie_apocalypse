# combat.py

class CombatHandler:
    
    @staticmethod
    def attack(executor, target):
        return executor.actor.attack(target)            

    @staticmethod
    def heal(executor, target):
        return executor.actor.heal(target)    