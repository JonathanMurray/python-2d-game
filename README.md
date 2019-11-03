# python-2d-game

This is a simple 2D action RPG game that lets you control a character and fight against 
different monsters, using potions and abilities to your advantage.

#### In-game footage (YoutTube):

[![in-game footage](https://img.youtube.com/vi/4FijOSF_O6o/0.jpg)](https://www.youtube.com/watch?v=4FijOSF_O6o)

#### Screenshots:

<img src="https://github.com/JonathanMurray/python-2d-game/blob/master/screenshots/gameplay.png" height="300" />
<br/>

_Choose your hero:_

<img src="https://github.com/JonathanMurray/python-2d-game/blob/master/screenshots/heroes.png" height="300" />
<br/>


_Master different abilities:_

<img src="https://github.com/JonathanMurray/python-2d-game/blob/master/screenshots/ability.png" height="300" />
<br/>

_Equip powerful items:_

<img src="https://github.com/JonathanMurray/python-2d-game/blob/master/screenshots/item.png" height="300" />
<br/>

_Customize your character with talents:_

<img src="https://github.com/JonathanMurray/python-2d-game/blob/master/screenshots/talents.png" height="300" />
<br/>


_Interact with NPCs:_

<img src="https://github.com/JonathanMurray/python-2d-game/blob/master/screenshots/dialog.png" height="300" />
<br/>

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

## Launching the map editor

Simply run
```
./map_editor.py
```
or to edit a specific map
```
./map_editor.py --map test.json
```

## Gameplay basics

* Use arrow keys to move
* Use keys shown in UI to use abilities and consumables
* Use spacebar to interact with NPCs and other entities in the environment
* Press 'Enter' to pause the game
* Press 'S' to save your progress

### Advanced usage
To play a specific map, run
```
./run.py --map test.json
```

or with a specific hero
```
./run.py --hero MAGE
./run.py --hero ROGUE
./run.py --hero WARRIOR
```

There may be more flags to use for debugging purposes.