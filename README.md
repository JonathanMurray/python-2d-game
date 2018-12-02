# python-2d-game

This is a simple 2D game that lets you control a character and fight against 
different monsters, using potions and abilities to your advantage.

It is very much a work in progress.

Look [here](todo.md) for future changes!

## Installation

This project uses Python3. 
 
The library [Pygame](https://www.pygame.org) is also used. 

To install pygame:
```
pip install -r requirements.txt
```

## Playing the game

Simply run
```
./run.py
```
or to play a specific map
```
./run.py resources/maps/demo.txt
```

## Launching the map editor

Simply run
```
./map_editor.py
```
or to edit a specific map
```
./map_editor.py resources/maps/demo.txt
```

## Gameplay basics

* Movement: use arrow keys
* Potions and abilities: use keys shown in the UI
* Pause game: press Enter
* Quit game: press Esc