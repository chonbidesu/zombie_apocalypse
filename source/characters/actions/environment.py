# environment.py

import pygame

class EnvironmentHandler:

    @staticmethod
    def close_doors(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_close"])                
            executor.action_progress.start("Closing doors", executor.block.close_doors)
        else:
            return executor.block.close_doors()
            
    @staticmethod
    def open_doors(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_open"])                
            executor.action_progress.start("Opening doors", executor.block.open_doors)
        else:
            return executor.block.open_doors()

    @staticmethod
    def barricade(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["barricade"])                
            executor.action_progress.start("Barricading", executor.block.barricade)
        else:
            return executor.block.barricade()

    @staticmethod
    def search(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["search"])                
            executor.action_progress.start("Searching", executor.block.search)
        else:
            return executor.block.search()

    @staticmethod
    def repair_building(executor, target):
        if executor.is_player:
            executor.action_progress.start("Repairing", executor.block.repair_building)
        else:
            return executor.block.repair_building()

    @staticmethod
    def decade(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["decade"])                
            executor.action_progress.start("Smashing", executor.block.decade)
        else:
            return executor.block.decade()
        
    @staticmethod
    def dump(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_close"])                
            executor.action_progress.start("Dumping body", executor.block.dump)
        else:
            return executor.block.dump()