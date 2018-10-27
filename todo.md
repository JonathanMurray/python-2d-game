## TODO

#### Refactorings:
* Move non-trivial logic from game_state. Prefer to have game-logic in main.py
* Reduce the ugly coupling between abilities and view.py

#### Game engine:
* Cooldown for using abilities
* Prevent using potion when at full stats

#### Features:
* More types of potions (mana potion, different strength, etc)
* More abilities (tmp movement speed, tmp health regen buff, AoE attack, etc)
* A message log
    * can show a message when an action fails (failed to use potion, can't 
    heal because already full health, etc)
* More enemies with different types of AI
* Save functionality
    * save the current game_state into a JSON file and load it on startup
* Introduce "items" (wearables that give you some buff)
    * Increased health/mana regen
    * Unlocks a new ability
    * Invisibility (enemies will not react to your presence)
