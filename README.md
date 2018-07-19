This is a python program that will randomize Pokemon Red. This randomizer will be focusing on procedural randomness, the eventual goal is being able to randomize the entire map so it's a completely new game, but still is beatable. The other goal of this is creating a good framework for a general randomizer that can be applied to any game.

## Getting Started

Prereq's:
* Python 3
* Whatever Pre-requisites [Pokemon Red Disassembly]() has

1) Clone this repository
1) Inside this repository, clone the [Pokemon Red]() disassembly.
1) Assuming all pre-req's are taken care of, run `python red.py <args>`

## Arguments (may be out of date, see `process` method of [red.py]() for up to date information)

### `-seed <value>`

Sets the seed of random to `value` before every randomization method

### starters

Randomizes the 3 starter pokemon in Oaks lab

### types

Randomizes the typing of every pokemon

### warps

Randomizes the locations that going through warps takes you (ala OOT Beta Quest Mod).

### connections

Randomizes the connections between overworld maps, currently doesn't use any logic when randomizing, so it's very probable to create inaccessible maps

### skip-intro

Does a number of things to speed up the intro of the game
* Shortens Oak's speech before the game starts
* Places the player in Oaks Lab at game start, being able to choose a pokemon right away
* Player no longer has to fight Blue in Oaks Lab
* Oak does not interrupt the player when they first step onto grass in Pallet Town

### wild

Randomly replaces every wild pokemon slot with a different random pokemon.

### build

Does nothing but build the current state of the repository. Useful for testing things manually

### rebuild

Does nothing, but causes the repository to be reset back to vanilla

### reorder-pokemon

Randomly reorganizes the constants in `pokemon_constants.asm`, messes up some sprites but the game seems playable.

### reorder-pokedex

Randomly reorganizes the constants in `pokedex_constants.asm`, completely messes up all pokemon sprites I have seen.