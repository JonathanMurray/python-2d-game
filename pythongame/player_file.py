import json
import os
from typing import Dict, List, Optional

from pythongame.core.common import Millis
from pythongame.core.game_state import PlayerState


class SavedPlayerState:
    def __init__(self, hero_id: str, level: int, exp: int, consumables_in_slots: Dict[str, List[str]],
                 items: List[List[str]], money: int, enabled_portals: Dict[str, str], talent_tier_choices: List[int],
                 total_time_played_on_character: Millis, active_quests: List[str], completed_quests: List[str]):
        self.hero_id = hero_id
        self.level = level
        self.exp = exp
        self.consumables_in_slots = consumables_in_slots
        self.items: List[List[str]] = items
        self.money = money
        self.enabled_portals = enabled_portals
        self.talent_tier_choices = talent_tier_choices
        self.total_time_played_on_character = total_time_played_on_character
        self.active_quests = active_quests
        self.completed_quests = completed_quests


class PlayerStateJson:
    @staticmethod
    def serialize(player_state: SavedPlayerState):
        return {
            "hero": player_state.hero_id,
            "level": player_state.level,
            "exp": player_state.exp,
            "consumables": player_state.consumables_in_slots,
            "items": player_state.items,
            "money": player_state.money,
            "enabled_portals": player_state.enabled_portals,
            "talents": player_state.talent_tier_choices,
            "total_time_played": player_state.total_time_played_on_character,
            "active_quests": player_state.active_quests,
            "completed_quests": player_state.completed_quests
        }

    @staticmethod
    def deserialize(data) -> SavedPlayerState:
        return SavedPlayerState(
            data["hero"],
            data["level"],
            data["exp"],
            data["consumables"],
            data["items"],
            data["money"],
            data["enabled_portals"],
            data.get("talents", []),
            data.get("total_time_played", 0),
            data.get("active_quests", []),
            data.get("completed_quests", []),
        )


class SaveFileHandler:

    def __init__(self):
        self.directory = "saved_characters"
        if not os.path.exists(self.directory):
            print("Save directory not found. Creating new directory: " + self.directory)
            os.makedirs(self.directory)

    def load_player_state_from_json_file(self, filename: str) -> SavedPlayerState:
        with open(self.directory + "/" + filename) as file:
            json_data = json.loads(file.read())
            return PlayerStateJson.deserialize(json_data)

    def _save_player_state_to_json_file(self, player_state: SavedPlayerState, filename: str):
        json_data = PlayerStateJson.serialize(player_state)
        with open(self.directory + "/" + filename, 'w') as file:
            file.write(json.dumps(json_data, indent=2))

    def save_to_file(self, player_state: PlayerState, existing_save_file: Optional[str],
                     total_time_played_on_character: Millis) -> str:
        if existing_save_file:
            filename = existing_save_file
        else:
            filename = self._generate_filename_for_new_character()
        saved_player_state = SavedPlayerState(
            hero_id=player_state.hero_id.name,
            level=player_state.level,
            exp=player_state.exp,
            consumables_in_slots={slot_number: [c.name for c in consumables] for (slot_number, consumables)
                                  in player_state.consumable_inventory.consumables_in_slots.items()},
            items=[[slot.get_item_id().stats_string, slot.get_item_id().name] if not slot.is_empty() else None
                   for slot in player_state.item_inventory.slots],
            money=player_state.money,
            enabled_portals={portal_id.name: sprite.name
                             for (portal_id, sprite) in player_state.enabled_portals.items()},
            talent_tier_choices=player_state.get_serilized_talent_tier_choices(),
            total_time_played_on_character=total_time_played_on_character,
            active_quests=[q.quest_id.name for q in player_state.active_quests],
            completed_quests=[q.quest_id.name for q in player_state.completed_quests]
        )
        self._save_player_state_to_json_file(saved_player_state, filename)
        print("Saved to file: " + filename)
        return filename

    def list_save_files(self):
        return os.listdir(self.directory)

    def _generate_filename_for_new_character(self):
        existing_files = self.list_save_files()
        if existing_files:
            id_from_filename = lambda f: int(f.split(".json")[0])
            existing_character_ids = [id_from_filename(f) for f in existing_files]
            next_available_id = max(existing_character_ids) + 1
        else:
            next_available_id = 1
        return str(next_available_id) + ".json"
