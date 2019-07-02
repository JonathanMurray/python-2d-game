## TODO

#### Refactorings:
* Move non-trivial logic from game_state. Prefer to have game-logic elsewhere.
* Avoid storing EnemyMind and ProjectileController in game_state. That module should only depend on common
* Simplify and generalise the handling of visual effects

#### Game engine:
* Use 8 directions instead of 4?
* Use pygame C code for vector math

#### Features:
* Different hero with different abilities
* Town portal to go back to start location 
    * consumable item?
    * item with ability (new concept)?
    * regular ability with long cooldown?
    * long cast-time, interrupted by dmg?
* Save functionality
    * save the current game_state into a JSON file and load it on startup
* More advanced abilities:
    * summon creatures to fight for you
    * debuffs that spread between enemies
    * effects that have a chance to trigger
    * effects that trigger if last-hitting an enemy
    * life-steal
    * buff that damages nearby enemies
    * buff that bounces damage back to enemies
* More advanced items
    * Unlocks a new ability
* Render enemy locations on minimap?
* more varied enemy AI
    * some enemies shouldn't aggro until very close
    * all enemies should at least wander around randomly when in sight