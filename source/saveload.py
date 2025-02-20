# saveload.py

import pickle
import os

from settings import *
from data import BLOCKS, ITEMS, ItemFunction, SaveLoadPath
from characters import CharacterName

class GameData:
    def __init__(self, game):
        self.city_data = self._serialize_city(game.state.city)
        self.player_data = self._serialize_player(game.state.player)
        self.npc_data = self._serialize_npcs(game.state.npcs)
        self.game_time = game.game_ui.description_panel.clock.time_in_minutes
        self.portrait = game.game_ui.status_panel.portrait_path

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
                    "is_known": block.is_known,
                }
                if properties.is_building:
                    block_data.update({
                        "block_inside_desc": block.block_inside_desc,
                        "lights_on": block.lights_on,
                        "generator_installed": block.generator_installed,
                        "ransack_level": block.ransack_level,
                        "ruined": block.ruined,
                        "fuel_expiration": block.fuel_expiration,
                        "barricade_level": block.barricade.level,
                        "barricade_sublevel": block.barricade.sublevel,
                    })
                city_data.append(block_data)
        return city_data

    def _serialize_player(self, player):
        return {
            "first_name": player.name.first_name,
            "last_name": player.name.last_name,
            "zombie_adjective": player.name.zombie_adjective,
            "occupation": player.occupation,
            "x": player.location[0],
            "y": player.location[1],
            "is_human": player.is_human,
            "is_dead": player.is_dead,
            "inside": player.inside,
            "hp": player.hp,
            "ap": player.ap,
            "xp": player.xp,
            "level": player.level,
            "human_skills": player.human_skills,
            "zombie_skills": player.zombie_skills,
            "inventory": [
                {
                    "type": item.type,
                    "is_equipped": item == player.weapon,
                    **item.get_attributes()
                }
                for item in player.inventory
            ],
        }

    def _serialize_npcs(self, npcs):
        npc_data = []

        for npc in npcs.list:
            npc_data.append({
            "first_name": npc.name.first_name,
            "last_name": npc.name.last_name,
            "zombie_adjective": npc.name.zombie_adjective,
            "occupation": npc.occupation,
            "x": npc.location[0],
            "y": npc.location[1],
            "is_human": npc.is_human,
            "is_dead": npc.is_dead,
            "inside": npc.inside,
            "hp": npc.hp,
            "ap": npc.ap,
            "xp": npc.xp,
            "level": npc.level,
            "human_skills": npc.human_skills,
            "zombie_skills": npc.zombie_skills,
            "inventory": [
                {
                    "type": item.type,
                    "is_equipped": item == npc.weapon,
                    **item.get_attributes()
                }
                for item in npc.inventory
            ],
        })

        return npc_data

    @classmethod
    def save_game(cls, index, game):
        """Save the game state to a file."""
        game_state = cls(game)

        # Get the correct save directory path
        file_path = SaveLoadPath(f"save_{index}.pkl").path

        # Save the game state
        with open(file_path, "wb") as file:
            pickle.dump(game_state, file)
        print("Game saved successfully.")

    @classmethod
    def load_game(cls, index):
        """Load the game state from a file."""
        file_path = SaveLoadPath(f"save_{index}.pkl").path

        try:
            with open(file_path, "rb") as file:
                game_state = pickle.load(file)
            print("Game loaded successfully.")
            return game_state
        except FileNotFoundError:
            print("Error: Save file not found.")
            return None

    def reconstruct_game(
        self, game, character_class, city_class, populate_class, 
        building_class, outdoor_class,
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
                block.barricade.sublevel = block_data["barricade_sublevel"]
                block.ransack_level = block_data["ransack_level"]
                block.ruined = block_data["ruined"]
            else:
                block = outdoor_class()

            block.type = block_type
            block.name = block_data["block_name"]
            block.block_outside_desc = block_data["block_outside_desc"]
            block.x = block_data["x"]
            block.y = block_data["y"]
            block.neighbourhood = block_data["neighbourhood"]
            block.is_known = block_data["is_known"]

            # Place the block in the correct position in the grid
            city.grid[block.y][block.x] = block


        # Reconstruct player
        first_name = self.player_data["first_name"]
        last_name = self.player_data["last_name"]
        zombie_adjective = self.player_data["zombie_adjective"]        
        name = CharacterName(first_name, last_name, zombie_adjective)
        
        player = character_class(
            game=game,
            name=name,
            occupation=self.player_data["occupation"],
            x=self.player_data["x"],
            y=self.player_data["y"],
            is_human=self.player_data["is_human"],
            inside=self.player_data["inside"],
        )
        
        # Reconstruct inventory
        for item_data in self.player_data["inventory"]:
            # Create item using the predefined method
            item = player.create_item(item_data["type"].name)

            # Restore additional attributes
            item_properties = ITEMS[item.type]
            if item_properties.item_function == ItemFunction.MELEE:  # For weapons, set weapon-specific attributes
                item.durability = item_data.get("durability", item.durability)
            if item_properties.item_function == ItemFunction.FIREARM:
                item.loaded_ammo = item_data.get("loaded_ammo", item.loaded_ammo)

            # Add item to the player's inventory
            player.inventory.append(item)

            # Check if the item is equipped
            if item_data.get("is_equipped", False):
                player.weapon = item

        for skill in self.player_data["human_skills"]:
            player.human_skills.add(skill)
        for skill in self.player_data["zombie_skills"]:
            player.zombie_skills.add(skill)

        player.hp = self.player_data.get("hp", player.max_hp)
        player.ap = self.player_data.get("ap", 0)
        player.xp = self.player_data.get("xp", 0)
        player.level = self.player_data.get("level", 1)
        player.is_dead = self.player_data.get("is_dead", False)

        if player.is_human:
            player.current_name = f"{player.name.first_name} {player.name.last_name}"
        else:
            player.current_name = f"{player.name.zombie_adjective} {player.name.first_name}"        

        # Create NPC list
        npcs = populate_class(game, total_humans=0, total_zombies=0)

        # Reconstruct NPCs
        for npc_data in self.npc_data:
            occupation=npc_data["occupation"]
            x=npc_data["x"]
            y=npc_data["y"]
            is_human=npc_data["is_human"]
            inside=npc_data["inside"]
            first_name = npc_data["first_name"]
            last_name = npc_data["last_name"]
            zombie_adjective = npc_data["zombie_adjective"]
            name = CharacterName(first_name, last_name, zombie_adjective)            

            npc = character_class(
                game=game, name=name, occupation=occupation, x=x, y=y, is_human=is_human, inside=inside,
            )

            # Reconstruct inventory
            for item_data in npc_data["inventory"]:
                # Create item using the predefined method
                item = npc.create_item(item_data["type"].name)

                # Restore additional attributes
                item_properties = ITEMS[item.type]
                if item_properties.item_function == ItemFunction.MELEE:  # For weapons, set weapon-specific attributes
                    item.durability = item_data.get("durability", item.durability)
                if item_properties.item_function == ItemFunction.FIREARM:
                    item.loaded_ammo = item_data.get("loaded_ammo", item.loaded_ammo)

                # Add item to the player's inventory
                npc.inventory.append(item)

                # Check if the item is equipped
                if item_data.get("is_equipped", False):
                    npc.weapon = item

            for skill in npc_data["human_skills"]:
                npc.human_skills.add(skill)
            for skill in npc_data["zombie_skills"]:
                npc.zombie_skills.add(skill)

            npc.hp = npc_data.get("hp", npc.max_hp)
            npc.ap = npc_data.get("ap", 0)
            npc.xp = npc_data.get("xp", 0)
            npc.level = npc_data.get("level", 1)
            npc.is_dead = npc_data.get("is_dead", False)

            if npc.is_human:
                npc.current_name = f"{npc.name.first_name} {npc.name.last_name}"
            else:
                npc.current_name = f"{npc.name.zombie_adjective} {npc.name.first_name}"

            npcs.list.append(npc)

        return player, city, npcs
