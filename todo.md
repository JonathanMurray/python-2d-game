## TODO

#### Refactorings:
* Move non-trivial logic from game_state. Prefer to have game-logic elsewhere.
* Avoid storing EnemyMind and ProjectileController in game_state. That module should only depend on common
* Simplify and generalise the handling of visual effects

#### Game engine:
* Use 8 directions instead of 4?
* Use pygame C code for vector math

#### Visuals:
* Render tiny buff icons above entities that have active buffs (like bloodlust icon from wc2)
* gray out ability icon when player doesn't have enough mana for it
* put dmg/healing/xp numbers further up for tall characters (base it on sprite size, not entity size)
* render action text further up for tall entities

#### Features:
* New heroes
    * stealthy swift rogue
        * invisibility, damage more from invis
        * prepares for fights by applying buffs
        * incapacitates strong enemies
        * poison bomb AoE ability, applies debuff
        * places traps on the ground, that deal dmg / stun when stepped upon
    * builder
        * place turret on ground that shoots in all directions
        * send out mechanical minion that seeks out enemies and self detonates
* Respawn on death
    * some fitting penalty
* Save functionality
    * save the current game_state into a JSON file and load it on startup
* More advanced abilities:
    * effects that trigger if last-hitting an enemy (execute ability, if it kills enemy then get mana back)
    * debuffs that spread between enemies
    * effects that have a chance to trigger
    * buff that damages nearby enemies
    * buff that bounces damage back to enemies
* More advanced items
    * Unlocks a new ability
* Render enemy locations on minimap?
* more varied enemy AI
    * some enemies shouldn't aggro until very close
    * all enemies should at least wander around randomly when in sight