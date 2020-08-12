import random
from typing import Type, Tuple

from pythongame.core.buff_effects import StatModifyingBuffEffect, register_buff_effect, AbstractBuffEffect, \
    get_buff_effect
from pythongame.core.common import Direction, BuffType, HeroStat, Millis
from pythongame.core.game_data import Sprite, register_entity_sprite_map, register_buff_text
from pythongame.core.game_state import PlayerState, GameState, NonPlayerCharacter
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.world_entity import WorldEntity

SHRINE_ENTITY_SIZE = (42, 39)

BUFF_DAMAGE = BuffType.SHRINE_DAMAGE
BUFF_ARMOR = BuffType.SHRINE_ARMOR
BUFF_MAGIC_RESIST = BuffType.SHRINE_MAGIC_RESIST
BUFF_MOVE_SPEED = BuffType.SHRINE_MOVE_SPEED

SHRINE_BUFFS = [BUFF_DAMAGE, BUFF_ARMOR, BUFF_MAGIC_RESIST, BUFF_MOVE_SPEED]

SHRINE_BUFF_DURATION = Millis(60_000)


# Only one shrine buff can be active at any one time
def cancel_existing_shrine_buffs(player_state: PlayerState, buff_type: BuffType):
    for other in [b for b in SHRINE_BUFFS if b != buff_type]:
        if player_state.has_active_buff(other):
            player_state.force_cancel_buff(other)


class AbstractShrineBuffEffect(StatModifyingBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        super().apply_start_effect(game_state, buffed_entity, buffed_npc)
        cancel_existing_shrine_buffs(game_state.player_state, self.buff_type)


class BuffDamage(AbstractShrineBuffEffect):
    def __init__(self):
        super().__init__(BUFF_DAMAGE, {HeroStat.DAMAGE: 0.25})


class BuffArmor(AbstractShrineBuffEffect):
    def __init__(self):
        super().__init__(BUFF_ARMOR, {HeroStat.ARMOR: 4})


class BuffMagicResist(AbstractShrineBuffEffect):
    def __init__(self):
        super().__init__(BUFF_MAGIC_RESIST, {HeroStat.MAGIC_RESIST_CHANCE: 0.25})


class BuffMoveSpeed(AbstractShrineBuffEffect):
    def __init__(self):
        super().__init__(BUFF_MOVE_SPEED, {HeroStat.MOVEMENT_SPEED: 0.25})


def register_shrines():
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    register_entity_sprite_map(Sprite.SHRINE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               {Direction.DOWN: [(14, 3)]}, (-7, -54))
    _register_buffs()


def _register_buffs():
    _register_buff(BUFF_DAMAGE, BuffDamage, "Shrine of Power")
    _register_buff(BUFF_ARMOR, BuffArmor, "Shrine of Protection")
    _register_buff(BUFF_MAGIC_RESIST, BuffMagicResist, "Shrine of Spirits")
    _register_buff(BUFF_MOVE_SPEED, BuffMoveSpeed, "Shrine of Swiftness")


def _register_buff(buff_type: BuffType, buff_class: Type[AbstractBuffEffect], buff_text: str):
    register_buff_effect(buff_type, buff_class)
    register_buff_text(buff_type, buff_text)


def _get_random() -> Tuple[AbstractBuffEffect, str]:
    return random.choice(
        [
            (get_buff_effect(BUFF_DAMAGE), "You feel powerful! (Damage increased)"),
            (get_buff_effect(BUFF_ARMOR), "You feel protected! (Armor increased)"),
            (get_buff_effect(BUFF_MAGIC_RESIST), "You feel the spirits' presence! (Resistance increased)"),
            (get_buff_effect(BUFF_MOVE_SPEED), "You feel swift! (Speed increased)")
        ]
    )


def apply_shrine_buff_to_player(player_state: PlayerState):
    buff_effect, text = _get_random()
    player_state.gain_buff_effect(buff_effect, SHRINE_BUFF_DURATION)
    return text
