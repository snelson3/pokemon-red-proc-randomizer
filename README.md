This is a python program that will randomize Pokemon Red. This randomizer will be focusing on procedural randomness, the eventual goal is being able to randomize the entire map so it's a completely new game, but still is beatable. The other goal of this is creating a good framework for a general randomizer that can be applied to any game.

## Getting Started

Prereq's:
* Python 3
* Whatever Pre-requisites [Pokemon Red Disassembly]() has

1) Clone this repository
1) Inside this repository, clone the [Pokemon Red]() disassembly.
1) Assuming all pre-req's are taken care of, run `python red.py <args>`

## Arguments (may be out of date, see `process` method of [red.py]() for up to date information)

### `seed <num>`

Sets the seed of random to `num`

### rebuild

Does nothing, is a dummy argument to make sure the process of building the rom works properly

### reorder-pokemon

Randomly reorganizes the constants in `pokemon_constants.asm`, messes up some sprites but the game seems playable.

### reorder-pokedex

Randomly reorganizes the constants in `pokedex_constants.asm`, completely messes up all pokemon sprites I have seen.