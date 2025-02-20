# movement.py

import pygame

class MovementHandler:
    
    @staticmethod
    def enter(executor, target):
        if executor.actor == executor.player and executor.block.barricade.can_pass(executor.actor):
            pygame.mixer.Sound.play(executor.game.sounds["footsteps"])                
            action_result = executor.screen_transition.circle_wipe(executor.actor.enter, executor.game.chat_history, executor.block)
        else:
            action_result = executor.actor.enter(executor.block)
        return action_result

    @staticmethod
    def leave(executor, target):
        if executor.actor == executor.player and executor.block.barricade.can_pass(executor.actor):
            pygame.mixer.Sound.play(executor.game.sounds["footsteps"])                
            action_result = executor.screen_transition.circle_wipe(executor.actor.leave, executor.game.chat_history, executor.block)
        else:
            action_result = executor.actor.leave(executor.block)
        return action_result


    @staticmethod
    def stand(executor, target):
        if executor.actor == executor.player:
            executor.action_progress.start("Standing", executor.player.stand, duration=10000)
        else:
            return executor.actor.stand()

    @staticmethod
    def move_up(executor, target):
        return executor.actor.move(0, -1)
    
    @staticmethod
    def move_down(executor, target):
        return executor.actor.move(0, 1)
    
    @staticmethod
    def move_left(executor, target):
        return executor.actor.move(-1, 0)
    
    @staticmethod
    def move_right(executor, target):
        return executor.actor.move(1, 0)
    
    @staticmethod
    def move_upleft(executor, target):
        return executor.actor.move(-1, -1)

    @staticmethod
    def move_upright(executor, target):
        return executor.actor.move(1, -1)
    
    @staticmethod
    def move_downleft(executor, target):        
        return executor.actor.move(-1, 1)
    
    @staticmethod
    def move_downright(executor, target):        
        return executor.actor.move(1, 1) 
          
    @staticmethod
    def move(executor, target):        
        dx, dy = target.dx, target.dy
        return executor.actor.move(dx, dy)
    
    @staticmethod
    def wander(executor, target):         
        return executor.actor.wander()                