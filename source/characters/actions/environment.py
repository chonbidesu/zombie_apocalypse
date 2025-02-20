# environment.py

import pygame

class EnvironmentHandler:

    @staticmethod
    def close_doors(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_close"])                
            executor.action_progress.start("Closing doors", executor.block.close_doors, executor.actor)
        else:
            return executor.block.close_doors(executor.actor)
            
    @staticmethod
    def open_doors(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_open"])                
            executor.action_progress.start("Opening doors", executor.block.open_doors, executor.actor)
        else:
            return executor.block.open_doors(executor.actor)

    @staticmethod
    def barricade(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["barricade"])                
            executor.action_progress.start("Barricading", executor.block.add_barricades, executor.actor)
        else:
            return executor.block.add_barricades(executor.actor)

    @staticmethod
    def search(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["search"])                
            executor.action_progress.start("Searching", executor.block.search, executor.actor)
        else:
            return executor.block.search(executor.actor)

    @staticmethod
    def repair_building(executor, target):
        if executor.is_player:
            executor.action_progress.start("Repairing", executor.block.repair_building, executor.actor)
        else:
            return executor.block.repair_building(executor.actor)

    @staticmethod
    def decade(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["decade"])                
            executor.action_progress.start("Smashing", executor.block.decade, executor.actor)
        else:
            return executor.block.decade(executor.actor)
        
    @staticmethod
    def ransack(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["decade"])                
            executor.action_progress.start("Ransacking", executor.block.ransack, executor.actor)
        else:
            return executor.block.ransack(executor.actor)        
        
    @staticmethod
    def dump(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_close"])                
            executor.action_progress.start("Dumping body", executor.block.dump, executor.actor)
        else:
            return executor.block.dump(executor.actor)