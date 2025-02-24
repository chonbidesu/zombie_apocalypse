# click_target.py


class ClickTarget:
    """Get the target of a mouse click."""
    def __init__(self, game, mouse_pos):
        self.type = None
        self.sprite = None
        self.human_sprite_group = game.game_ui.description_panel.human_sprite_group
        self.zombie_sprite_group = game.game_ui.description_panel.zombie_sprite_group
        self.viewport_group = game.game_ui.viewport.viewport_group
        self.inventory_group = game.game_ui.inventory_panel.inventory_group
        self.player_portrait = game.game_ui.status_panel.player_sprite
        
        self.get(mouse_pos)

    def get(self, mouse_pos):
        """Get the target of a mouse click, saving the sprite and returning the target type."""
        for sprite in self.viewport_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'block'
        for sprite in self.inventory_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite  
                self.type = 'item'
        for sprite in self.zombie_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'zombie'
        for sprite in self.human_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'human'
        if self.player_portrait.rect.collidepoint(mouse_pos):
            self.sprite = self.player_portrait
            self.type = 'self'
        if self.type == None:
            self.type = 'screen'  