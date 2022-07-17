import random
from math import floor
from util import *

"""
Analysis functions
"""
all_rounds = []


def save_round_results(results):
    all_rounds.append(results)


"""
Gameplay Functions
"""


def make_piles(cards, n_piles):
    piles = [[] for _ in range(n_piles + 1)]  # init blank piles, one extra to hold jokers
    for i in range(1, n_piles + 1):
        for j in range(i, len(piles)):
            if cards:
                piles[j].append(cards.pop(0))
            else:
                return piles, cards
    return piles, cards


def adjust_piles(piles, verbose=False):
    while True:
        tops = get_tops(piles)
        if verbose:
            print(f"\nTops: {tops}")
            pprint_piles(piles)

        # Move jokers
        if 0 in tops:
            pile_num = tops.index(0) + 1
            piles[0].append(piles[pile_num].pop(0))
            if verbose:
                print(f"Moved joker from pile {pile_num}")
            continue

        # Move duplicate card
        if duplicates_in_list(tops, ignore=[-1]):
            for card in tops:
                found_at = [i for i, j in enumerate(piles) if piles[i] and piles[i][0] == card]
                if len(found_at) > 1:
                    # Count the number of face down cards in each pile with the duplicate card on top
                    n_face_down = [len(piles[i]) - count_face_up(piles[i]) for i in found_at]

                    # Find the pile with fewest & most face down cards
                    small_index = found_at[n_face_down.index(min(n_face_down))]
                    big_index = found_at[n_face_down.index(max(n_face_down))]
                    if small_index == big_index:  # if the piles are the same size, move to the left-most pile
                        small_index = found_at[0]
                        big_index = found_at[1]
                    big_pile = piles[big_index]
                    small_pile = piles[small_index]

                    # Move the top card from the big pile over to the small pile (where size is measured by # face down)
                    small_pile.insert(0, big_pile.pop(0))

                    if verbose:
                        print(f"Moved {card} from pile {big_index}, to pile {small_index}")
                    break
            continue

        # If there are any empty piles & face down cards to fill them
        if tops.count(-1) > 0 and sum(counts_face_down(piles)) != 0:
            # find empty pile
            empty_pile_index = piles[1:].index([]) + 1  # plus one to account for joker pile

            # Find biggest pile -- "pile size" is measured by the number of face down cards
            pile_sizes = [len(pile) - count_face_up(pile) for pile in piles]
            biggest_pile_size = max(pile_sizes)

            # If there are no cards to fill the empty piles with, we're done!
            if biggest_pile_size == 0:
                if verbose:
                    print("Final state")
                return piles

            biggest_pile_index = pile_sizes.index(biggest_pile_size)

            # Move all face up cards from the biggest pile into the empty pile
            n_to_move = count_face_up(piles[biggest_pile_index])
            piles[empty_pile_index] = piles[biggest_pile_index][:n_to_move]
            piles[biggest_pile_index] = piles[biggest_pile_index][n_to_move:]
            if verbose:
                pprint_piles(piles)
                print("Filled empty pile")

        # If there are no duplicates, and no jokers, and no empty piles that need filling, we're done!
        else:
            if verbose:
                print("Done adjusting")
            return piles


def check_moves(piles, discards):
    for p in piles:
        for d in discards:
            if p and d and are_neighbors(d[0], p[0]):
                return True
    return False


# A series of hands, at the end of which someone has no cards.
class Round:
    def __init__(self, halves):
        self.player1, self.left_deck = make_piles(halves[0], 5)
        self.player2, self.right_deck = make_piles(halves[1], 5)
        self.left_discard = []
        self.right_discard = []

    def print_board(self, xray=False):
        player1 = self.player1
        player2 = self.player2
        left_discard = self.left_discard
        right_discard = self.right_discard
        left_deck = self.left_deck
        right_deck = self.right_deck

        print("\nBOARD STATE")
        print(f"{'[*]' * len(left_deck)}")
        print(left_discard)
        print(right_discard)
        print(f"{'[*]' * len(right_deck)}")
        print("\nPlayer 1")
        pprint_piles(player1, xray=xray)
        print("\nPlayer 2")
        pprint_piles(player2, xray=xray)

    def play_hand(self, strategy):
        player1 = self.player1
        player2 = self.player2
        left_discard = self.left_discard
        right_discard = self.right_discard
        left_deck = self.left_deck
        right_deck = self.right_deck

        # Flip cards
        if left_deck:
            left_discard.insert(0, left_deck.pop(0))
        if right_deck:
            right_discard.insert(0, right_deck.pop(0))

        # Race!
        while True:
            # See who can play
            p1_has_moves = check_moves(player1, [left_discard, right_discard])
            p2_has_moves = check_moves(player2, [left_discard, right_discard])

            # If both can play, roll initiative
            if p1_has_moves and p2_has_moves:
                fastest_player = random.choice(["player1", "player2"])
            # Otherwise, the only one who can play takes a turn
            elif p1_has_moves or p2_has_moves:
                fastest_player = "player1" if p1_has_moves else "player2"
            # If no one can play, time to start a new hand
            else:
                break

            if fastest_player == 'player1':
                player1, left_discard, right_discard = self.play_card(player1, [left_discard, right_discard],
                                                                      strategy=strategy)
            else:
                player2, left_discard, right_discard = self.play_card(player2, [left_discard, right_discard],
                                                                      strategy=strategy)

            # If someone won with this play, stop!
            winner = Round.find_winner([player1, player2])
            if winner:
                break

    @staticmethod
    def play_card(piles, discard_piles, strategy, verbose=False):
        play_on = None  # the discard pile to play a card on
        play_from = None  # the pile to play from

        order = strategy(piles)
        for i in order:
            if piles[i]:
                top = piles[i][0]
                can_play_left = False if not discard_piles[0] else are_neighbors(top, discard_piles[0][0])
                can_play_right = False if not discard_piles[1] else are_neighbors(top, discard_piles[1][0])
                # TODO: Optimize joker value selection
                if can_play_left and can_play_right:
                    play_on = random.choice([0, 1])
                    play_from = i
                    continue  # stop as soon as we find a move
                elif can_play_left or can_play_right:
                    play_on = 0 if can_play_left else 1
                    play_from = i
                    continue  # stop as soon as we find a move

        if verbose:
            print("Before playing")
            pprint_piles(piles)
            print(discard_piles)
            print("Playing...")

        # Get the card to play
        card_to_play = piles[play_from].pop(0)

        # If it's a joker, declare it to be one of the neighboring cards, whichever would allow you to play again
        # FIXME: This differs from the IRL rules
        if card_to_play == 0:
            card_to_play = Round.choose_joker_value(piles, discard_piles)

        # Play the card
        discard_piles[play_on].insert(0, card_to_play)

        # adjust piles
        piles = adjust_piles(piles)

        if verbose:
            pprint_piles(piles)
            print(discard_piles)

        # return new piles & new discard piles
        return piles, discard_piles[0], discard_piles[1]

    def play(self, round_strategy, verbose=True):
        player1 = adjust_piles(self.player1)
        player2 = adjust_piles(self.player2)
        left_discard = self.left_discard
        right_discard = self.right_discard
        left_deck = self.left_deck
        right_deck = self.right_deck

        # Play hands until someone wins, or you run out of cards
        winner = None
        while not winner and (left_deck or right_deck):
            self.play_hand(round_strategy)
            winner = Round.find_winner([player1, player2])
        if not winner:
            pass  # TODO: handle a "tie" (i.e. running out of cards to flip before anyone wins)

        if verbose:
            self.print_board(xray=True)
            print(f"WINNER: Player {winner}")

        return {"winner": winner, "player1": player1, "player2": player2,
                "left_deck": left_deck, "right_deck": right_deck,
                "left_discard": left_discard, "right_discard": right_discard}

    # Prioritize opening a second move, then turning over cards
    @staticmethod
    def _prioritize_next_move(piles):
        tops = get_tops(piles)
        priority_piles = []
        for t in tops:
            for c in tops:
                if are_neighbors(t, c):
                    pile_num = tops.index(t) + 1
                    priority_piles.append(pile_num)

        # Order piles by priority first, number of face-down cards second
        pile_sizes = counts_face_down(piles)
        order = sorted(range(len(pile_sizes)), key=lambda k: pile_sizes[k] + int(k in priority_piles) * len(piles),
                       reverse=True)

        # Move joker pile to after the priority piles
        order.remove(0)
        order.insert(len(priority_piles), 0)
        return order
    prioritize_next_move = _prioritize_next_move

    @staticmethod
    def _prioritize_revealing_cards(piles):
        # Put piles in order of most unturned cards
        pile_sizes = counts_face_down(piles)
        order = sorted(range(len(pile_sizes)), key=lambda k: pile_sizes[k], reverse=True)
        # Add joker at the end
        order.remove(0)
        order.append(0)
        return order
    prioritize_revealing_cards = _prioritize_revealing_cards

    @staticmethod
    def _choose_joker_value(piles, discard_piles):
        tops = get_tops(piles)
        discards = [pile[0] for pile in discard_piles if pile]
        for discard in discards:
            neighbors = get_neighbors(discard)
            for n in neighbors:
                if n != 0:
                    second_neighbors = get_neighbors(n)
                    for m in second_neighbors:
                        if m in tops:
                            return n

        return random.choice(get_neighbors(random.choice(discards)))
    choose_joker_value = _choose_joker_value

    @staticmethod
    def _find_winner(players):
        for i, piles in enumerate(players):
            # If they have all empty piles, winner!
            if piles.count([]) == len(piles):
                return i + 1
        return None  # if both have cards, return None
    find_winner = _find_winner


# A set of rounds played with a single shuffle
class Game:
    BALANCED_STRATEGY_THRESHOLD = 5  # TODO EXPERIMENT WITH THIS

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

        if pile_size_diff < Game.BALANCED_STRATEGY_THRESHOLD:
            return Game.winner_takes_own(results)
        return Game.winner_takes_smallest(results)

    def play(self, winner_strategy, round_strategy, verbose=False):
        sudden_death = False
        p1_half, p2_half = cut(self.deck, 2)
        results, last_winner = None, None
        while True:
            if verbose:
                print(f"Player 1 starring with {len(p1_half)} cards")
                print(f"Player 2 starting with {len(p2_half)} cards")

            # If someone has only enough cards for their piles (or fewer), it's sudden death!
            if len(p1_half) < 16 or len(p2_half) < 16:
                sudden_death = True
                if verbose:
                    print(f"\nSUDDEN DEATH: Last winner was Player {last_winner}")

            r = Round([p1_half, p2_half])
            results = r.play(round_strategy=round_strategy, verbose=verbose)

            save_round_results(results)

            last_winner = results["winner"]
            if sudden_death:
                if results["winner"] == last_winner:
                    return results  # Declare game victory
                else:
                    sudden_death = False
                    if verbose:
                        print(f"AN UPSET!! YOU CAN DO IT, PLAYER {results['winner']}")

            p1_half, p2_half = winner_strategy(results)


"""
Play a bunch of matches
"""
winners = []
for g in range(100):
    game = Game()
    game_results = game.play(winner_strategy=Game.winner_takes_smallest, round_strategy=Round.prioritize_next_move)
    winners.append(game_results["winner"])

print(all_rounds)
print(f"MATCH RESULTS\nPlayer 1: {winners.count(1)}\nPlayer 2: {winners.count(2)}\nTie: {winners.count(None)}")


"""
Test
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
