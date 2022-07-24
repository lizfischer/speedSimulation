from util import *
from game import Game
from round import Round
from player import Player


"""
MATCH SETTINGS
"""

NUMBER_OF_GAMES = 200  # How many games to play in a row
INTERACTIVE = False  # set to True if you want to step through the game play-by-play (hit space to advance)
VERBOSE = False  # set to True if you want the steps of the game printed out while it runs, but not wait for you

""" Round strategies 
How players decide which cards to play during a round of gameplay. The options are:
    Round.prioritize_next_move 
    Round.prioritize_revealing_cards
Prioritizing next move means the player prefers to play cards which will allow them to play another card after.
Prioritizing revealing cards means the player prefers to play card from whichever pile has the most face-down cards.   
 """
p1_round_strategy = Round.prioritize_next_move
p2_round_strategy = Round.prioritize_next_move

""" Game strategies
How players decide which stack of cards to take at the end of a game, if they won. The options are:
    Game.winner_takes_smallest
    Game.winner_takes_own
    Game.winner_takes_balanced
Winner takes smallest means the winning player takes whichever stack of cards is smaller.
Winner takes own means the winning player takes whichever stack of cards they've been flipping cards into.
Winner takes balanced means the winning player will take their own pile when the difference in pile size is small. 

You can set the threshold for the balanced strategy with Game.BALANCED_STRATEGY_THRESHOLD. This number determines the 
largest difference in pile size players will tolerate before they stop taking their own pile. 
E.g. P1's strategy is balanced and the threshold is set to 5, they will take their own pile
as long as it is no more than 5 cards larger than P2's
"""
p1_game_strategy = Game.winner_takes_smallest
p2_game_strategy = Game.winner_takes_balanced

Game.BALANCED_STRATEGY_THRESHOLD = 2


"""
Match Loop
(Play a bunch of games)
"""
winners = []
for g in range(NUMBER_OF_GAMES):
    game = Game()
    player1 = Player(round_strategy=Round.prioritize_next_move, game_strategy=Game.winner_takes_smallest)
    player2 = Player(round_strategy=Round.prioritize_next_move, game_strategy=Game.winner_takes_balanced)
    game_results = game.play(player1, player2, verbose=VERBOSE, interactive=INTERACTIVE)
    winners.append(game_results["winner"])


print(f"MATCH RESULTS\n"
      f"Player 1: {winners.count(1)} "
      f"\tRound strategy: {player1.round_strategy.__name__}, Game Strategy: {player1.game_strategy.__name__}\n"
      f"Player 2: {winners.count(2)}"
      f"\tRound strategy: {player2.round_strategy.__name__}, Game Strategy: {player2.game_strategy.__name__}"
      f"\nTie: {winners.count(None)}")


"""
Test starter decks
"""
# test_pile = [2, 0, 2, 2, 2, 2, 13, 13, 2, 13, 0, 7, 2, 2, 2,  # pile adjustment edge cases
test = [2, 0, 2, 7, 12, 8, 13, 13, 5, 11, 0, 7, 10, 1, 9,  # player 1 piles
        6, 4, 3, 7, 8, 6, 5, 13, 13, 9, 10, 4,  # left deck
        4, 12, 4, 1, 6, 11, 7, 5, 3, 10, 9, 10, 11, 2, 11,  # player 2 piles
        9, 1, 1, 12, 8, 2, 5, 12, 3, 6, 3, 8]  # right deck
test2 = [11, 1, 6, 7, 3, 2, 6, 0, 6, 0, 3, 1, 12, 9, 9,
         12, 6, 1, 8, 5, 8, 10, 12, 2, 7, 2, 4,
         1, 3, 5, 4, 5, 11, 10, 11, 10, 8, 7, 9, 11, 4, 9,
         12, 8, 7, 3, 13, 13, 13, 5, 2, 10, 4, 13]
test3 = [7, 13, 4, 3, 7, 13, 0, 8, 3, 10, 5, 11, 6, 10, 13, 7, 2, 9, 2, 6, 8, 5, 12, 3, 1, 12, 10, 2, 5, 13, 11, 9, 0,
         12, 10, 12, 1, 2, 8, 9, 6, 1, 7, 5, 1, 11, 3, 9, 4, 11, 4, 8, 6, 4]

test_piles = [[], [2], [8, 2], [7, 12, 0], [13, 13, 5, 11], [10, 0, 7, 1, 9]]
# prioritize_next_move(test_piles, discard_piles=[[6], [12]])
