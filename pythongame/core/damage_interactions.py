from pythongame.core.common import SoundId, Millis
from pythongame.core.enemy_target_selection import EnemyTarget
from pythongame.core.game_state import NonPlayerCharacter, GameState, WorldEntity, BuffNotification
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import create_visual_damage_text, VisualRect, create_visual_healing_text


# Returns
# True if damage was dealt.
# False if enemy was invulnerable.
def deal_player_damage_to_enemy(game_state: GameState, npc: NonPlayerCharacter, base_amount: float):
    player_state = game_state.player_state
    damage_modifier: float = player_state.base_damage_modifier + player_state.damage_modifier_bonus
    amount: float = base_amount * damage_modifier
    if npc.invulnerable:
        return False
    npc.lose_health(amount)
    game_state.visual_effects.append(create_visual_damage_text(npc.world_entity, int(round(amount))))
    health_from_life_steal = player_state.life_steal_ratio * amount
    health_gained = player_state.gain_health(health_from_life_steal)
    if health_gained > 0:
        game_state.visual_effects.append(create_visual_healing_text(game_state.player_entity, health_gained))
    return True


def deal_damage_to_player(game_state: GameState, amount: float):
    health_lost = game_state.player_state.lose_health(amount)
    if health_lost > 0:
        game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, health_lost))
        play_sound(SoundId.PLAYER_PAIN)
        game_state.player_state.notify_buffs(BuffNotification.player_lost_health(health_lost))


def deal_npc_damage_to_npc(game_state: GameState, target: NonPlayerCharacter, amount: float):
    target.lose_health(amount)
    rounded_amount = round(amount)
    if rounded_amount > 0:
        game_state.visual_effects.append(create_visual_damage_text(target.world_entity, rounded_amount))


def deal_npc_damage(damage_amount: float, game_state: GameState, attacker_entity: WorldEntity, target: EnemyTarget):
    attacker_position = attacker_entity.get_center_position()
    game_state.visual_effects.append(
        VisualRect((200, 0, 0), attacker_position, 50, 50, Millis(200), 3, attacker_entity))
    if target.non_enemy_npc:
        deal_npc_damage_to_npc(game_state, target.non_enemy_npc, damage_amount)
    else:
        deal_damage_to_player(game_state, damage_amount)
