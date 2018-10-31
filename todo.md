## TODO

#### Refactorings:
* Move non-trivial logic from game_state. Prefer to have game-logic in main.py

#### Game engine:
* Use 8 directions instead of 4?
* Introduce obstacles that block enemies
* Prevent enemies from walking through each other

#### Features:
* Introduce more varied functionality for different projectiles
    * arrow that explodes on impact?
    * cloud that deals damage continuously?
* New advanced enemy behaviors
    * summoning new enemies?
* Enemy AI and enemy interactions that make a bit more sense
* Save functionality
    * save the current game_state into a JSON file and load it on startup
* Introduce "items" (wearables that give you some buff)
    * Increased health/mana regen
    * Unlocks a new ability
    * Invisibility (enemies will not react to your presence)
