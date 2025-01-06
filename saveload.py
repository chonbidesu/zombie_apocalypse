# saveload.py

import pickle
import pygame
from collections import defaultdict

class GameState:
    def __init__(self, player, city, zombie_group):
        self.city_data = self._serialize_city(city)
        self.player_data = self._serialize_player(player)
        self.zombie_data = self._serialize_zombies(zombie_group)

    def _serialize_city(self, city):
        city_data = {
            "blocks": [],
            "neighbourhoods": city.neighbourhood_groups.keys(),
        }
        for y, group in enumerate(city.y_groups):
            for block in group:
                block_data = {
                    "x": city.x_groups.index(block),
                    "y": y,
                    "block_type": block.block_type,
                    "block_name": block.block_name,
                    "block_desc": block.block_desc,
                    "zoom_x": getattr(block, "zoom_x", None),
                    "zoom_y": getattr(block, "zoom_y", None),
                }
                city_data["blocks"].append(block_data)
        return city_data

    def _serialize_player(self, player):
        return {
            "x": player.location[0],
            "y": player.location[1],
            "inside": player.inside,
            "inventory": [
                {
                    "item_type": item.item_type,
                    "name": item.name,
                    "attributes": item.get_attributes(),  # Assumes a method to serialize attributes
                }
                for item in player.inventory
            ],
        }

    def _serialize_zombies(self, zombie_group):
        zombie_data = []
        for zombie in zombie_group:
            zombie_data.append({
                "x": zombie.get_coordinates()[0],
                "y": zombie.get_coordinates()[1],
                "inside": zombie.inside,
            })
        return zombie_data

    @classmethod
    def save_game(cls, file_path, player, city, zombie_group):
        """Save the game state to a file."""
        game_state = cls(player, city, zombie_group)
        with open(file_path, "wb") as file:
            pickle.dump(game_state, file)
        print("Game saved successfully.")

    @classmethod
    def load_game(cls, file_path):
        """Load the game state from a file."""
        with open(file_path, "rb") as file:
            game_state = pickle.load(file)
        print("Game loaded successfully.")
        return game_state

    def reconstruct_game(self, player_class, city_class, zombie_class, item_class):
        """Reconstruct the game objects."""
        # Reconstruct city
        city = city_class(self.city_data["neighbourhoods"])
        for block_data in self.city_data["blocks"]:
            block = city.add_block(
                x=block_data["x"],
                y=block_data["y"],
                block_type=block_data["block_type"],
                block_name=block_data["block_name"],
                block_desc=block_data["block_desc"],
                zoom_x=block_data["zoom_x"],
                zoom_y=block_data["zoom_y"],
            )

        # Reconstruct player
        player = player_class(
            city=city,
            x=self.player_data["x"],
            y=self.player_data["y"],
            inside=self.player_data["inside"],
        )
        for item_data in self.player_data["inventory"]:
            item = item_class(
                item_type=item_data["item_type"],
                name=item_data["name"],
                attributes=item_data["attributes"],
            )
            player.inventory.add(item)

        # Reconstruct zombies
        zombie_group = pygame.sprite.Group()
        for zombie_data in self.zombie_data:
            zombie = zombie_class(
                city=city,
                x=zombie_data["x"],
                y=zombie_data["y"],
                inside=zombie_data["inside"],
            )
            zombie_group.add(zombie)

        return player, city, zombie_group
