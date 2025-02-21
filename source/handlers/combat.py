# combat.py

class CombatHandler:
    
    @staticmethod
    def attack(executor, target):
        return executor.actor.state.attack(target)

    @staticmethod
    def heal(executor, target):
        return executor.actor.state.heal(target)    
    
    @staticmethod
    def extract_dna(executor, target):
        return executor.actor.state.extract_dna(target)
    
    @staticmethod
    def inject(executor, target):
        return executor.actor.state.inject(target) 
    
    @staticmethod
    def speak(executor, target):
        return executor.actor.state.speak(target)