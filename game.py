from util import *
from round import Round


# A set of rounds played with a single shuffle
class Game:
    BALANCED_STRATEGY_THRESHOLD = 5

    def __init__(self, deck=None):
        self.deck = deck
        if not deck:
            self.deck = create_deck()
            random.shuffle(self.deck)

    @staticmethod
    def winner_takes_smallest(results):
        # Create new "halves"
        p1_half = results["left_deck"] + flatten(results["player1"])
        p2_half = results["right_deck"] + flatten(results["player2"])

        # Determine which discard pile is smaller
        if len(results["left_discard"]) > len(results["right_discard"]):
            smaller_pile = results["right_discard"]
            bigger_pile = results["left_discard"]
        elif len(results["right_discard"]) > len(results["left_discard"]):
            smaller_pile = results["left_discard"]
            bigger_pile = results["right_discard"]
        else:
            p1_half += results["left_discard"]
            p2_half += results["right_discard"]
            return [p1_half, p2_half]

        if results["winner"] == 1:  # Player 1 won
            p1_half += smaller_pile
            p2_half += bigger_pile
        elif results["winner"] == 2:  # Player 2 won
            p2_half += smaller_pile
            p1_half += bigger_pile
        else:  # Impasse
            p1_half += results["left_discard"]
            p2_half += results["right_discard"]
        return p1_half, p2_half

    @staticmethod
    def winner_takes_own(results):
        p1_half = results["left_deck"] + results["left_discard"] + flatten(results["player1"])
        p2_half = results["right_deck"] + results["right_discard"] + flatten(results["player2"])
        return p1_half, p2_half

    @staticmethod
    def winner_takes_balanced(results):
        pile_size_diff = abs(len(results["left_discard"]) - len(results["right_discard"]))

        if pile_size_diff <= Game.BALANCED_STRATEGY_THRESHOLD:
            return Game.winner_takes_own(results)
        return Game.winner_takes_smallest(results)

# Game.winner_takes_smallest
# Game.winner_takes_own
# Game.winner_takes_balanced
# Game.BALANCED_STRATEGY_THRESHOLD

    def play(self, player1, player2, verbose=False, interactive=False):
        sudden_death = False
        p1_half, p2_half = cut(self.deck, 2)
        results, last_winner = None, None
        while True:
            if verbose:
                print(f"Player 1 starring with {len(p1_half)} cards")
                print(f"Player 2 starting with {len(p2_half)} cards")
                if interactive:
                    input()

            # If someone has only enough cards for their piles (or fewer), it's sudden death!
            if len(p1_half) < 16 or len(p2_half) < 16:
                sudden_death = True
                if verbose:
                    print(f"\nSUDDEN DEATH: Last winner was Player {last_winner}")

            # Reset the Jokers # TODO: FINISH FIXING THIS SHIT
            p1_half = [x if x < 100 else 100 for x in p1_half]
            p2_half = [x if x < 100 else 100 for x in p2_half]

            # Initiate new round
            r = Round(player1, player2, [p1_half, p2_half], interactive=interactive)
            results = r.play(player1, player2, verbose=verbose, interactive=interactive)

            save_round_results(results)

            last_winner = results["winner"]
            if sudden_death:
                if results["winner"] == last_winner:
                    return results  # Declare game victory
                else:
                    sudden_death = False
                    if verbose:
                        print(f"AN UPSET!! YOU CAN DO IT, PLAYER {results['winner']}")

            if results["winner"] == 1:
                p1_half, p2_half = player1.game_strategy(results)
            elif results["winner"] == 2:
                p1_half, p2_half = player2.game_strategy(results)
            else:
                p1_half, p2_half = Game.winner_takes_own(results)
                #raise Exception("No one won that round, how do we decide how to proceed?")
