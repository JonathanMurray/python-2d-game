#!/usr/bin/env python3

import math
import pygame
import sys
from enum import Enum

class Box:
	def __init__(self, pos, size, color):
		self.x = pos[0]
		self.y = pos[1]
		self.w = size[0]
		self.h = size[1]
		self.color = color

	def rect(self):
		return (self.x, self.y, self.w, self.h)

class MovingBox:
	def __init__(self, box, direction, speed, max_speed):
		self.box = box
		self.direction = direction
		self.speed = speed
		self.max_speed = max_speed

	def set_moving_in_dir(self, direction):
		self.direction = direction
		self.speed = self.max_speed

	def set_not_moving(self):
		self.speed = 0

class Direction(Enum):
	LEFT = 1
	RIGHT = 2
	UP = 3
	DOWN = 4

class PlayerStats:
	def __init__(self, health, max_health, mana, max_mana):
		self.health = health
		self.max_health = max_health
		self.mana = mana
		self.mana_float = mana
		self.max_mana = max_mana

	def gain_health(self, amount):
		self.health = min(self.health + amount, self.max_health)

	def lose_health(self, amount):
		player_stats.health -= amount

	def gain_mana(self, amount):
		self.mana_float = min(self.mana_float + amount, self.max_mana)
		self.mana = int(math.floor(self.mana_float))

	def lose_mana(self, amount):
		self.mana_float -= amount
		self.mana = int(math.floor(self.mana_float))

def render_box(screen, box, camera_pos):
	pygame.draw.rect(screen, box.color, (box.x - camera_pos[0], box.y - camera_pos[1], box.w, box.h))

def ranges_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)

def boxes_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
    	and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)

def render_stat_bar(screen, x, y, w, h, stat, max_stat, color):
	pygame.draw.rect(screen, (250, 250, 250), (x - 2, y - 2, w + 3, h + 3), 2)
	pygame.draw.rect(screen, color, (x, y, w * stat / max_stat, h))

def update_moving_box_position(moving_box, collide_with_game_boundary):
	if moving_box.direction == Direction.LEFT:
		moving_box.box.x -= moving_box.speed
	elif moving_box.direction == Direction.RIGHT:
		moving_box.box.x += moving_box.speed
	elif moving_box.direction == Direction.UP:
		moving_box.box.y -= moving_box.speed
	elif moving_box.direction == Direction.DOWN:
		moving_box.box.y += moving_box.speed
	if collide_with_game_boundary:
		moving_box.box.x = min(max(moving_box.box.x, 0), GAME_WORLD_SIZE[0] - moving_box.box.w)
		moving_box.box.y = min(max(moving_box.box.y, 0), GAME_WORLD_SIZE[1] - moving_box.box.h)

BG_COLOR = (200,200,200)
SCREEN_SIZE = (500,500)
CAMERA_SIZE = (500, 430)
GAME_WORLD_SIZE = (600,600)
GAME_WORLD_BOX = Box((0, 0), GAME_WORLD_SIZE, (0,0,0))
FOOD_SIZE = (30, 30)
FOOD_COLOR = (50, 200, 50)
ENEMY_SIZE = (50, 50)
ENEMY_COLOR = (250, 0, 0)

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
screen = pygame.display.set_mode(SCREEN_SIZE)

camera_pos = (0, 0)
player = MovingBox(Box((100, 100), (50, 50), (250,250,250)), Direction.RIGHT, 0, 9)
projectiles = []
food_boxes = [Box(pos, FOOD_SIZE, FOOD_COLOR) for pos in [(150, 350), (450, 300), (560, 550), (30, 520), \
	(200, 500), (300, 500), (410, 420)]]
enemy_boxes = [Box(pos, ENEMY_SIZE, ENEMY_COLOR) for pos in [(320, 220), (370, 320), (420, 10)]]
player_stats = PlayerStats(3, 20, 6, 15)
heal_mana_cost = 3
attack_mana_cost = 5

while(True):

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				player.set_moving_in_dir(Direction.LEFT)
			elif event.key == pygame.K_RIGHT:
				player.set_moving_in_dir(Direction.RIGHT)
			elif event.key == pygame.K_UP:
				player.set_moving_in_dir(Direction.UP)
			elif event.key == pygame.K_DOWN:
				player.set_moving_in_dir(Direction.DOWN)
			elif event.key == pygame.K_a:
				if player_stats.mana >= heal_mana_cost:
					player_stats.lose_mana(heal_mana_cost)
					player_stats.gain_health(10)
			elif event.key == pygame.K_f:
				if player_stats.mana >= attack_mana_cost:
					player_stats.lose_mana(attack_mana_cost)
					projectiles.append(MovingBox(Box((player.box.x, player.box.y), (50, 50), (200, 5, 200)), player.direction, 4, 4))
		if event.type == pygame.KEYUP:
			player.set_not_moving()

	update_moving_box_position(player, True)
	projectiles_to_delete = []
	for projectile in projectiles:
		update_moving_box_position(projectile, False)
		if not boxes_intersect(projectile.box, GAME_WORLD_BOX):
			projectiles_to_delete.append(projectile)
	projectiles = [p for p in projectiles if p not in projectiles_to_delete]

	camera_pos = (min(max(player.box.x - CAMERA_SIZE[0] / 2, 0), GAME_WORLD_SIZE[0] - CAMERA_SIZE[0]), \
		min(max(player.box.y - CAMERA_SIZE[1] / 2, 0), GAME_WORLD_SIZE[1] - CAMERA_SIZE[1]))

	food_boxes_to_delete = []
	for box in food_boxes:
		if boxes_intersect(player.box, box):
			food_boxes_to_delete.append(box)
			player_stats.gain_health(1)
	food_boxes = [b for b in food_boxes if b not in food_boxes_to_delete]
	enemy_boxes_to_delete = []
	for box in enemy_boxes:
		if boxes_intersect(player.box, box):
			enemy_boxes_to_delete.append(box)
			player_stats.lose_health(2)
	enemy_boxes = [b for b in enemy_boxes if b not in enemy_boxes_to_delete]

	player_stats.gain_mana(0.03)

	screen.fill(BG_COLOR)
	for box in food_boxes + enemy_boxes + [player.box] + [p.box for p in projectiles]:
		render_box(screen, box, camera_pos)
	pygame.draw.rect(screen, (0, 0, 0), (0, 0, CAMERA_SIZE[0], CAMERA_SIZE[1]), 3)
	pygame.draw.rect(screen, (0, 0, 0), (0, CAMERA_SIZE[1], SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))

	render_stat_bar(screen, 10, 440, 100, 25, player_stats.health, player_stats.max_health, (250, 0, 0))
	render_stat_bar(screen, 130, 440, 100, 25, player_stats.mana, player_stats.max_mana, (0, 0, 250))

	ui_text = "[" + str(player_stats.health) + "/" + str(player_stats.max_health) + "] " + \
		"[" + str(player_stats.mana) + "/" + str(player_stats.max_mana) + "] " + \
		"['A' to heal (" + str(heal_mana_cost) + ")] " + \
		"['F' to attack (" + str(attack_mana_cost) + ")]"
	text_surface = font.render(ui_text, False, (250, 250, 250))
	screen.blit(text_surface, (20, 475))
	
	pygame.display.update()

