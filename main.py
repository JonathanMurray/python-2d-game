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

class PlayerBox:
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

def rects_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
    	and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)

BG_COLOR = (200,200,200)
SCREEN_SIZE = (500,500)
CAMERA_SIZE = (500, 470)
GAME_WORLD_SIZE = (600,600)
FOOD_SIZE = (30, 30)
FOOD_COLOR = (50, 200, 50)
ENEMY_SIZE = (50, 50)
ENEMY_COLOR = (250, 0, 0)

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
screen = pygame.display.set_mode(SCREEN_SIZE)

camera_pos = (0, 0)
player = PlayerBox(Box((100, 100), (50, 50), (250,250,250)), Direction.RIGHT, 0, 9)
food_boxes = [Box(pos, FOOD_SIZE, FOOD_COLOR) for pos in [(150, 350), (450, 300), (560, 550), (30, 520), \
	(200, 500), (300, 500), (410, 420)]]
enemy_boxes = [Box(pos, ENEMY_SIZE, ENEMY_COLOR) for pos in [(320, 220), (370, 320), (420, 10)]]
player_stats = PlayerStats(3, 20, 6, 15)
heal_mana_cost = 3

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
		if event.type == pygame.KEYUP:
			player.set_not_moving()

	if player.direction == Direction.LEFT:
		player.box.x = max(player.box.x - player.speed, 0)
	elif player.direction == Direction.RIGHT:
		player.box.x = min(player.box.x + player.speed, GAME_WORLD_SIZE[0] - player.box.w)
	elif player.direction == Direction.UP:
		player.box.y = max(player.box.y - player.speed, 0)
	elif player.direction == Direction.DOWN:
		player.box.y = min(player.box.y + player.speed, GAME_WORLD_SIZE[1] - player.box.h)

	camera_pos = (min(max(player.box.x - CAMERA_SIZE[0] / 2, 0), GAME_WORLD_SIZE[0] - CAMERA_SIZE[0]), \
		min(max(player.box.y - CAMERA_SIZE[1] / 2, 0), GAME_WORLD_SIZE[1] - CAMERA_SIZE[1]))


	food_boxes_to_delete = []
	for box in food_boxes:
		if rects_intersect(player.box, box):
			food_boxes_to_delete.append(box)
			player_stats.gain_health(1)
	food_boxes = [b for b in food_boxes if b not in food_boxes_to_delete]

	enemy_boxes_to_delete = []
	for box in enemy_boxes:
		if rects_intersect(player.box, box):
			enemy_boxes_to_delete.append(box)
			player_stats.lose_health(2)
	enemy_boxes = [b for b in enemy_boxes if b not in enemy_boxes_to_delete]

	player_stats.gain_mana(0.01)

	screen.fill(BG_COLOR)
	render_box(screen, player.box, camera_pos)
	for box in food_boxes + enemy_boxes:
		render_box(screen, box, camera_pos)
	pygame.draw.rect(screen, (0, 0, 0), (0, 0, CAMERA_SIZE[0], CAMERA_SIZE[1]), 3)
	pygame.draw.rect(screen, (0, 0, 0), (0, CAMERA_SIZE[1], SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
	ui_text = "[" + str(player_stats.health) + "/" + str(player_stats.max_health) + " HP]   " + \
		"[" + str(player_stats.mana) + "/" + str(player_stats.max_mana) + " mana]   " + \
		"['A' to heal (" + str(heal_mana_cost) + "mana)]"

	text_surface = font.render(ui_text, False, (250, 250, 250))
	screen.blit(text_surface, (20, 475))
	pygame.display.update()

