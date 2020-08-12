from enum import Enum


class QuestId(Enum):
    MAIN_RETRIEVE_KEY = 1
    RETRIEVE_FROG = 2
    RETRIEVE_CORRUPTED_ORB = 3


class Quest:
    def __init__(self, quest_id: QuestId, name: str, description: str):
        self.quest_id = quest_id
        self.name = name
        self.description = description
