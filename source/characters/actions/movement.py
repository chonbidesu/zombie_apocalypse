# movement.py

import pygame

class MovementHandler:
    
    @staticmethod
    def enter(executor, target):
        if executor.is_player and executor.block.barricade.can_pass(executor.actor):
            pygame.mixer.Sound.play(executor.game.sounds["footsteps"])                
            action_result = executor.screen_transition.circle_wipe(executor.player.state.enter, executor.game.chat_history)
        else:
            action_result = executor.actor.state.enter()
        return action_result

    @staticmethod
    def leave(executor, target):
        if executor.is_player and executor.block.barricade.can_pass(executor.actor):
            pygame.mixer.Sound.play(executor.game.sounds["footsteps"])                
            action_result = executor.screen_transition.circle_wipe(executor.player.state.leave, executor.game.chat_history)
        else:
            action_result = executor.actor.state.leave()
        return action_result


    @staticmethod
    def stand(executor, target):
        if executor.is_player:
            executor.action_progress.start("Standing", executor.player.state.stand, duration=10000)
        else:
            return executor.actor.state.stand()

    @staticmethod
    def move_up(executor, target):
        return executor.actor.state.move(0, -1)
    
    @staticmethod
    def move_down(executor, target):
        return executor.actor.state.move(0, 1)
    
    @staticmethod
    def move_left(executor, target):
        return executor.actor.state.move(-1, 0)
    
    @staticmethod
    def move_right(executor, target):
        return executor.actor.state.move(1, 0)
    
    @staticmethod
    def move_upleft(executor, target):
        return executor.actor.state.move(-1, -1)

    @staticmethod
    def move_upright(executor, target):
        return executor.actor.state.move(1, -1)
    
    @staticmethod
    def move_downleft(executor, target):        
        return executor.actor.state.move(-1, 1)
    
    @staticmethod
    def move_downright(executor, target):        
        return executor.actor.state.move(1, 1) 
          
    @staticmethod
    def move(executor, target):        
        dx, dy = target.dx, target.dy
        return executor.actor.state.move(dx, dy)
    
    @staticmethod
    def wander(executor, target):         
        return executor.actor.state.wander()                