## TODO

#### Refactorings:
* Move non-trivial logic from game_state. Prefer to have game-logic in main.py
* 

#### Features:
* More types of potions (mana potion, different strength, etc)
* More abilities (tmp movement speed, tmp health regen buff, AoE attack, etc)
* A message log
    * can show a message when an action fails (failed to use potion, can't 
    heal because already full health, etc)
* More enemies with different types of AI
* Save functionality
    * save the current game_state into a JSON file and load it on startup
