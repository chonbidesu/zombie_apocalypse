# saveload.py

import pickle
import pygame
from collections import defaultdict

from settings import *

class Gamestate:
    def __init__(self, player):
        self.city_data = self._serialize_city(player.city)
        self.player_data = self._serialize_player(player)
        self.zombie_data = self._serialize_zombies(player.zombie_group)

    def _serialize_city(self, city):
        city_data = {
            "blocks": [],
            "neighbourhoods": list(city.neighbourhood_groups.keys()),
        }
        for y, group in enumerate(city.y_groups):
            for block in group:
                if block in city.cityblock_group:
                    x = next(
                        (x_index for x_index, x_group in enumerate(city.x_groups) if block in x_group),
                        None,
                    )
                    if x is None:
                        raise ValueError(f"Block {block} not found in x_groups")
                    
                    block_data = {
                        "x": x,
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
                    "name": item.name,
                    "is_equipped": item in player.weapon,
                    **item.get_attributes()
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
    def save_game(cls, file_path, player):
        """Save the game state to a file."""
        game_state = cls(player)
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

    def reconstruct_game(self, player_class, city_class, zombie_class, item_class, building_class, outdoor_class, button_group,
                         create_xy_groups, update_observations, get_block_at_player, get_block_at_xy,   
    ):
        """Reconstruct the game objects."""
        # Reconstruct city
        x_groups, y_groups = create_xy_groups()
        city = city_class(x_groups, y_groups)
        button_group = button_group

        # Clear x_groups and y_groups
        for i in range(100):
            city.x_groups[i].empty()
            city.y_groups[i].empty()

        # Reconstruct blocks
        for block_data in self.city_data["blocks"]:
            block_type = block_data["block_type"]
            if block_type in BUILDING_TYPES:
                block = building_class()
                city.building_group.add(block)
                city.building_type_groups[block_type].add(block)
            else:
                block = outdoor_class()
                city.outdoor_group.add(block)
                city.outdoor_type_groups[block_type].add(block)

            block.block_type = block_type
            block.block_name = block_data["block_name"]
            block.block_desc = block_data["block_desc"]
            block.zoom_x = block_data.get("zoom_x")
            block.zoom_y = block_data.get("zoom_y")
            block.generate_descriptions(city.descriptions, block_type)

            x = block_data["x"]
            y = block_data["y"]
            city.x_groups[x].add(block)
            city.y_groups[y].add(block)
            city.cityblock_group.add(block)

        # Reconstruct neighbourhood groups
        for neighbourhood_name in self.city_data["neighbourhoods"]:
            neighbourhood_group = pygame.sprite.Group()
            for y_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE):
                for x_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE):
                    for y in range(y_start, y_start + NEIGHBOURHOOD_SIZE):
                        for x in range(x_start, x_start + NEIGHBOURHOOD_SIZE):
                            block = next(
                                (b for b in city.x_groups[x] if b in city.y_groups[y]),
                                None,
                            )
                            if block:
                                neighbourhood_group.add(block)
            city.neighbourhood_groups[neighbourhood_name] = neighbourhood_group

        # Reconstruct player
        player = player_class(
            city=city,
            x_groups=city.x_groups,
            y_groups=city.y_groups,
            button_group=button_group,
            update_observations = update_observations,
            get_block_at_player = get_block_at_player,
            name=self.player_data.get("name", "Player"),
            occupation=self.player_data.get("occupation", "Survivor"),
            x=self.player_data["x"],
            y=self.player_data["y"],
            inside=self.player_data["inside"],
        )
        
        for item_data in self.player_data["inventory"]:
            item = item_class(name=item_data["name"])

            _ = item._image # Trigger lazy-loading of images

            player.inventory.add(item)

            if "durability" in item_data:
                item.durability = item_data["durability"]
            if "loaded_ammo" in item_data:
                item.loaded_ammo = item_data["loaded_ammo"]

            if item_data.get("is_equipped", False):
                player.weapon.add(item)

                if item_data["name"] in MELEE_WEAPONS:
                    player.weapon_group.add(item)
                    player.melee_group.add(item)
                elif item_data["name"] in FIREARMS:
                    player.weapon_group.add(item)
                    player.firearm_group.add(item)


        player.hp = self.player_data.get("hp", player.max_hp)
        player.ticker = self.player_data.get("ticker", 0)

        # Reconstruct zombies
        zombie_group = pygame.sprite.Group()
        for zombie_data in self.zombie_data:
            x = zombie_data["x"]
            y = zombie_data["y"]
            inside = zombie_data["inside"]

            zombie = zombie_class(
                player=player,
                get_block_at_xy=get_block_at_xy,
                x=x,
                y=y,
            )
            zombie.inside = inside
            zombie.hp = zombie_data.get("hp", ZOMBIE_START_HP)
            zombie.action_points = zombie_data.get("action_points", 0)
            zombie.is_dead = zombie_data.get("is_dead", False)


        return player, city, zombie_group
