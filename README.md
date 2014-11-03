Battleground
========================================================================

## Table of contents ##
- [Introduction](#introduction)
- [System configuration](#system-configurations)
- [Game rules](#game-rules)

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
The user must define a class called `Bot` that implements the method evaluate_turn wich receives the following parameters:


