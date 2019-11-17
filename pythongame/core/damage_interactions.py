import math
import random
from enum import Enum
from typing import Optional

from pythongame.core.common import SoundId, Millis
from pythongame.core.enemy_target_selection import EnemyTarget
from pythongame.core.game_state import NonPlayerCharacter, GameState, WorldEntity, PlayerLostHealthEvent, \
    PlayerDamagedEnemy, PlayerWasAttackedEvent, PlayerBlockedEvent
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import create_visual_damage_text, VisualRect, create_visual_healing_text, \
    create_visual_mana_text, create_visual_block_text, create_visual_dodge_text


class DamageType(Enum):
    PHYSICAL = 1
    MAGIC = 2


# Returns
# True if damage was dealt.
# False if enemy was invulnerable.
# damage_source parameter can be used to prevent buffs from triggering themselves
def deal_player_damage_to_enemy(game_state: GameState, npc: NonPlayerCharacter, base_amount: float,
                                visual_emphasis: bool = False, damage_source: Optional[str] = None):
    player_state = game_state.player_state
    damage_modifier: float = player_state.base_damage_modifier + player_state.damage_modifier_bonus
    amount: float = base_amount * damage_modifier
    if npc.invulnerable:
        return False
    health_lost_integer = npc.health_resource.lose(amount)
    game_state.player_state.notify_about_event(PlayerDamagedEnemy(npc, damage_source), game_state)
    game_state.visual_effects.append(
        create_visual_damage_text(npc.world_entity, health_lost_integer, emphasis=visual_emphasis))
    health_from_life_steal = player_state.life_steal_ratio * amount
    player_receive_healing(health_from_life_steal, game_state)
    return True


def deal_damage_to_player(game_state: GameState, base_amount: float, damage_type: DamageType,
                          npc_attacker: Optional[NonPlayerCharacter]):
    player_state = game_state.player_state
    if npc_attacker:
        player_state.notify_about_event(PlayerWasAttackedEvent(npc_attacker), game_state)
    damage_reduction = 0
    # Armor only reduces physical damage
    if damage_type == DamageType.PHYSICAL:
        dodge_chance = player_state.base_dodge_chance + player_state.dodge_chance_bonus
        if random.random() < dodge_chance:
            game_state.visual_effects.append(create_visual_dodge_text(game_state.player_entity))
            damage_reduction = base_amount  # Somewhat of a hack. All damage is mitigated when dodging
        elif random.random() < player_state.block_chance:
            if player_state.block_damage_reduction > 0:
                game_state.visual_effects.append(create_visual_block_text(game_state.player_entity))
            damage_reduction += player_state.block_damage_reduction
            player_state.notify_about_event(PlayerBlockedEvent(npc_attacker), game_state)
        # Armor has a random element to it. Example: 5 armor absorbs 0-5 damage
        damage_reduction += random.randint(0, math.floor(player_state.base_armor) + player_state.armor_bonus)
    amount = max(0.0, base_amount - damage_reduction)
    health_lost_integer = player_state.health_resource.lose(amount)
    if health_lost_integer > 0:
        game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, health_lost_integer))
        play_sound(SoundId.ENEMY_ATTACK)
        if random.random() < 0.3:
            play_sound(SoundId.PLAYER_PAIN)
        player_state.notify_about_event(PlayerLostHealthEvent(health_lost_integer, npc_attacker), game_state)
    else:
        play_sound(SoundId.ENEMY_ATTACK_WAS_BLOCKED)


def deal_npc_damage_to_npc(game_state: GameState, target: NonPlayerCharacter, amount: float):
    health_lost_integer = target.health_resource.lose(amount)
    if health_lost_integer > 0:
        game_state.visual_effects.append(create_visual_damage_text(target.world_entity, health_lost_integer))


def deal_npc_damage(damage_amount: float, damage_type: DamageType, game_state: GameState, attacker_entity: WorldEntity,
                    attacker_npc: NonPlayerCharacter, target: EnemyTarget):
    attacker_position = attacker_entity.get_center_position()
    game_state.visual_effects.append(
        VisualRect((200, 0, 0), attacker_position, 50, 50, Millis(200), 3, attacker_entity))
    if target.non_enemy_npc:
        deal_npc_damage_to_npc(game_state, target.non_enemy_npc, damage_amount)
    else:
        deal_damage_to_player(game_state, damage_amount, damage_type, attacker_npc)


def player_receive_healing(healing_amount: float, game_state: GameState):
    health_gained_integer = game_state.player_state.health_resource.gain(healing_amount)
    if health_gained_integer > 0:
        game_state.visual_effects.append(create_visual_healing_text(game_state.player_entity, health_gained_integer))


def player_receive_mana(mana_amount: float, game_state: GameState):
    mana_gained_integer = game_state.player_state.mana_resource.gain(mana_amount)
    if mana_gained_integer > 0:
        game_state.visual_effects.append(create_visual_mana_text(game_state.player_entity, mana_gained_integer))
