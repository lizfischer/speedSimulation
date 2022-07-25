# Speed Simulation

This is a simulation of the card game Speed.

## Requirements
Python 3.8

## Running the code
Clone or download this repository. 
Change settings in `speed.py`, then from a terminal window run `python speed.py`
See below (or comments in `speed.py` for and explanation of the settings)

## Terminology
Some lingo that'll make reading the code easier
- **Piles**: the stacks of cards from which cards are played. Each player has 5 piles at the start of a round.
- **Left/Right Deck**: the stacks of face-down cards placed in the middle at the start of a round, after players have made their piles. The directions "left" and "right" are just convenient... assume that the players are sitting on the same side of the table.
- **Left/Right Discard**: the piles of cards in the middle onto which other cards are played.
- **Hand**: the fast-paced part when people are playing cards. A hand ends when new cards need to be flipped 
  onto the discard piles from the deck.
- **Round**: a series of hands, which ends with one player having no cards left in their piles. The winner of a round 
  gets to choose which discard pile they want to keep.
- **Game**: a series of rounds, which ends with one player having no cards left in their side 
of the deck & is declared the winner.
- **Match**: a series of games.

## Available settings
### General match settings
- `-NUMBER_OF_GAMES = 200`: How many games to play in a row
- `INTERACTIVE = False`: set to `True` if you want to step through the game play-by-play (hit space to advance)
- `VERBOSE = False`: set to `True` if you want the steps of the game printed out while it runs, but not wait for you

### Round strategies 
How players decide which cards to play during a round of gameplay. The options are:
    
- `Round.prioritize_next_move`
- `Round.prioritize_revealing_cards`

Prioritizing next move means the player prefers to play cards which will allow them to play another card after.
Prioritizing revealing cards means the player prefers to play card from whichever pile has the most face-down cards.   

```
p1_round_strategy = Round.prioritize_next_move
p2_round_strategy = Round.prioritize_revealing_cards
```

### Game strategies
How players decide which stack of cards to take at the end of a game, if they won. The options are:
    
- `Game.winner_takes_smallest`
- `Game.winner_takes_own`
- `Game.winner_takes_balanced`

Winner takes smallest means the winning player takes whichever stack of cards is smaller.
Winner takes own means the winning player takes whichever stack of cards they've been flipping cards into.
Winner takes balanced means the winning player will take their own pile when the difference in pile size is small. 

You can set the threshold for the balanced strategy by changing the value of `Game.BALANCED_STRATEGY_THRESHOLD`. 
This number determines the largest difference in pile size players will tolerate before they stop taking their own pile. 
E.g. P1's strategy is balanced and the threshold is set to 5, they will take their own pile
as long as it is no more than 5 cards larger than P2's
```
p1_game_strategy = Game.winner_takes_smallest
p2_game_strategy = Game.winner_takes_balanced

Game.BALANCED_STRATEGY_THRESHOLD = 2
```
