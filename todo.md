## TODO

#### Refactorings:
* Move non-trivial logic from game_state. Prefer to have game-logic elsewhere.
* Avoid storing EnemyMind and ProjectileController in game_state. That module should only depend on common
* Simplify and generalise the handling of visual effects
* Simplify how channeled abilities work - shouldn't need to define new buff types for that
* Use PeriodicTimer in enemy behaviour code, to reduce time-keeping boilerplate
* Clean up enemy movement/attack logic - model as FSM?

#### Game engine:
* Use 8 directions instead of 4?
* save game_state to file on crash
* Make it more difficult to kite fast enemies. Enemies are too slow at attacking when they get into melee range

#### Visuals:
* Render tiny buff icons above entities that have active buffs (like bloodlust icon from wc2)
* gray out ability icon when player doesn't have enough mana for it
* put dmg/healing/xp numbers further up for tall characters (base it on sprite size, not entity size)
* render action text further up for tall entities
* use transparent sprite when hero is stealthed
* render stat bonuses with green color
* show more clearly in UI, which inventory slots are storage and which ones are for equipped items

#### Sounds:
* Abilities
    * mage channeling ability
* UI
    * drop potion or item
* using portal
* goblin death sounds

#### Features:
* right click items to swap them between inventory and equipped
* allow some type of items to be stacked in inventory (gold nugget and sapphire)
* give enemies 'armor'?
    * could add effects that reduce armor on enemies
    * makes it more difficult to clear endgame content on low level
* New heroes
    * builder
        * place turret on ground that shoots in all directions
        * send out mechanical minion that seeks out enemies and self detonates
* New "progress" functionality:
    * choosing between different abilities on level-up
    * gaining a more powerful version of an existing ability. Whirlwind could start without stun and then gain stun on upgrade
* More advanced abilities:
    * AoE effect that covers a large area and stays after being cast (like Diablo 2 sorc Blizzard ability)
    * channeling locked in one target. drain life / slow / gain mana / gain damage bonus
    * effects that trigger if last-hitting an enemy (execute ability, if it kills enemy then get mana back)
    * debuffs that spread between enemies
    * effects that have a chance to trigger
    * buff that damages nearby enemies
    * buff that bounces damage back to enemies
* Render enemy locations on minimap?
* more varied enemy AI
    * some enemies shouldn't aggro until very close
    * all enemies should at least wander around randomly when in sight