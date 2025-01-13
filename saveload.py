# saveload.py

import pickle

from settings import *

class Gamestate:
    def __init__(self, player, city, zombies):
        self.city_data = self._serialize_city(city)
        self.player_data = self._serialize_player(player)
        self.zombie_data = self._serialize_zombies(zombies)

    def _serialize_city(self, city):
        city_data = []
        for row in city.grid:
            for block in row:
                properties = BLOCKS[block.type]
                block_data = {
                    "x": block.x,
                    "y": block.y,
                    "block_type": block.type,
                    "block_name": block.name,
                    "block_outside_desc": block.block_outside_desc,
                    "neighbourhood": block.neighbourhood,
                }
                if properties.is_building:
                    block_data.update({
                        "block_inside_desc": block.block_inside_desc,
                        "lights_on": block.lights_on,
                        "generator_installed": block.generator_installed,
                        "is_ransacked": block.is_ransacked,
                        "fuel_expiration": block.fuel_expiration,
                        "barricade_level": block.barricade.level,
                        "barricade_health": block.barricade.health,
                    })
                city_data.append(block_data)
        return city_data

    def _serialize_player(self, player):
        return {
            "name": player.name,
            "occupation": player.occupation,
            "x": player.location[0],
            "y": player.location[1],
            "inside": player.inside,
            "hp": player.hp,
            "ticker": player.ticker,
            "skills": player.skills,
            "inventory": [
                {
                    "type": item.type,
                    "is_equipped": item in player.weapon,
                    **item.get_attributes()
                }
                for item in player.inventory
            ],
        }

    def _serialize_zombies(self, zombies):
        zombie_data = []
        for zombie in zombies.list:
            zombie_data.append({
                "x": zombie.location[0],
                "y": zombie.location[1],
                "inside": zombie.inside,
                "is_dead": zombie.is_dead,
                "action_points": zombie.action_points,
                "hp": zombie.hp,
            })
        return zombie_data

    @classmethod
    def save_game(cls, file_path, player, city, zombies):
        """Save the game state to a file."""
        game_state = cls(player, city, zombies)
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

    def reconstruct_game(self, player_class, city_class, zombie_class, zombulate_class, 
                         building_class, outdoor_class, chat_history,
    ):
        """Reconstruct the game objects."""
        # Reconstruct city
        city = city_class()
        city.grid = [[None for _ in range(CITY_SIZE)] for _ in range(CITY_SIZE)]

        # Reconstruct and replace city grid
        for block_data in self.city_data:
            block_type = block_data["block_type"]
            properties = BLOCKS[block_type]
            if properties.is_building:
                block = building_class()
                block.block_inside_desc = block_data["block_inside_desc"]
                block.lights_on = block_data["lights_on"]
                block.generator_installed = block_data["generator_installed"]
                block.fuel_expiration = block_data["fuel_expiration"]
                block.barricade.set_barricade_level(block_data["barricade_level"])
                block.barricade.health = block_data["barricade_health"]
                block.is_ransacked = block_data["is_ransacked"]
            else:
                block = outdoor_class()

            block.type = block_type
            block.name = block_data["block_name"]
            block.block_outside_desc = block_data["block_outside_desc"]
            block.x = block_data["x"]
            block.y = block_data["y"]
            block.neighbourhood = block_data["neighbourhood"]

            # Place the block in the correct position in the grid
            city.grid[block.y][block.x] = block


        # Reconstruct player
        player = player_class(
            city=city,
            name=self.player_data.get("name", "Player"),
            occupation=self.player_data.get("occupation", "Survivor"),
            x=self.player_data["x"],
            y=self.player_data["y"],
            inside=self.player_data["inside"],
        )
        
        # Reconstruct inventory
        for item_data in self.player_data["inventory"]:
            # Create item using the predefined method
            item = player.create_item(item_data["type"])
            properties = ITEMS[item.type]
            item.image_file = properties.image_file

            # Restore additional attributes
            if properties.item_function == ItemFunction.MELEE:  # For weapons, set weapon-specific attributes
                item.durability = item_data.get("durability", item.durability)
            if properties.item_function == ItemFunction.FIREARM:
                item.loaded_ammo = item_data.get("loaded_ammo", item.loaded_ammo)

            # Add item to the player's inventory
            player.inventory.add(item)

            # Check if the item is equipped
            if item_data.get("is_equipped", False):
                player.weapon.add(item)

        player.hp = self.player_data.get("hp", player.max_hp)
        player.ticker = self.player_data.get("ticker", 0)

        # Create zombie list
        zombies = zombulate_class(player, city, chat_history, total_zombies=0)

        # Reconstruct zombies
        for zombie_data in self.zombie_data:
            x = zombie_data["x"]
            y = zombie_data["y"]
            inside = zombie_data["inside"]

            zombie = zombie_class(
                player=player, city=city, chat_history=chat_history, x=x, y=y,
            )
            zombie.inside = inside
            zombie.hp = zombie_data.get("hp", ZOMBIE_MAX_HP)
            zombie.action_points = zombie_data.get("action_points", 0)
            zombie.is_dead = zombie_data.get("is_dead", False)
            zombies.list.append(zombie)

        return player, city, zombies
