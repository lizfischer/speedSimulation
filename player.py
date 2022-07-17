from util import *

"""
Player: A container for piles & some strategy preferences
"""


class Player:
    def __init__(self, round_strategy, game_strategy):
        self.round_strategy = round_strategy
        self.game_strategy = game_strategy
        self.piles = None

    """ Saves piles to self, returns the extra cards """
    def make_piles(self, cards, n_piles):
        piles = [[] for _ in range(n_piles + 1)]  # init blank piles, one extra to hold jokers
        for i in range(1, n_piles + 1):
            for j in range(i, len(piles)):
                if cards:
                    piles[j].append(cards.pop(0))
                else:
                    self.piles = piles
                    return cards
        self.piles = piles
        return cards

    """ Saves adjusted piles to self """
    def adjust_piles(self, verbose=False):
        piles = self.piles
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
                    self.piles = piles
                    return

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
                self.piles = piles
                return
