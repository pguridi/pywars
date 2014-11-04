Battleground
========================================================================

## Table of contents ##
- [Introduction](#introduction)
- [System configuration](#system-configurations)
- [Game rules](#game-rules)
    - [Programming the tank bot](#programming-the-tank-bot)

## Introduction ##

A turn based tank game for Python bots


## System configuration ##
This is the configuration for development. Make sure you have a virtualenv. You need to do the following:
* Install the dependencies running `pip install -r requirements.txt`
* Create the database running `python manage.py migrate`
* Create an admin user with `python manage.py createsuperuser`
* Run the development server `python manage.py runserver`
* Open the browser at `http://127.0.0.1:8000/`


## Game rules ##
The game is simple, you will program a tank-bot that should destroy the oponent's tank. The game is by turns, and in each turn the tank has three possible actions to make:
  * **Shoot**: The tank can fire a projectile against its enemy target. That will cause two possible results:
    - The projectile hits the enemy, reducing his live by a certain amount.
    - The projectile miss and nothing happens.
  * **Move**: The tank can move forward or move back, but only one step per turn.
  * **Do Nothing**: Pretty self explanatory. Nothing happens here.

The game ends when one of the tanks is destroyed, i.e: his live reachs 0 points, or when 250 turns are played, in which case the tank who wins is the tank who has more live when the turns went off.

### Programming the tank bot ###
The user must define a class called `Bot` that implements the method `evaluate_turn` wich receives the following parameters:
* `arena_array`: An array with the positions of the players in the battleground. For     example an array containing `[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0]` where the     numbers are the tank ids and the position in the array its location.
* `feedback`: The result of the previous turn. For example, for the shoot action     'SUCESS' is returned if the enemy is hit, and 'FAILED' otherwise.
* `life`: Current tank life. A number between 0-100.

The method then should return a dictionary indicating what the tank will do in its turn. For this, the player has a few options:
  * **Move**: For this the player must return a dictionary like this `{'ACTION': 'MOVE', 'WHERE': 1}` where 1 is for moving forward and -1 is for moving back.
  * **Shoot**: For this the player must return a dictionary like this `{'ACTION': 'SHOOT', 'ANGLE': 35, 'VEL': 100}` where the values of _ANGLE_ must be between _0_ and _89_ and the _VEL_ values must be between _0_ and _100_.
  * **Stay**: The player decides not doing anything so it returns an empty dictionary.

## IMPORTANT ##
The code used to implement `evaluate_turn` must run in **PyPy**. For security reasons, the code runs in a PyPy Sandbox, so keep in mind that modules like `random` or `time` are not available, so you must figure out how to live with that :P
