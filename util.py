import random
from math import floor

"""
Analysis functions
"""
all_rounds = []


def save_round_results(results):
    all_rounds.append(results)


"""
Utility Functions
"""


def create_deck():
    deck = [0, 0]
    for value in range(1, 14):
        for _ in ['diamonds', 'clubs', 'spades', 'hearts']:
            deck.append(value)
    return deck


def cut(cards, n_piles):
    pile_size = floor(len(cards) / n_piles)
    remainder = len(cards) - (n_piles * pile_size)
    piles = []
    for i in range(0, n_piles):
        start = i * pile_size
        end = (i + 1) * pile_size
        if i < remainder:
            end += 1
        piles.append(cards[start:end])
    return piles


def pprint_piles(piles, xray=False):
    s = ""
    for p in piles:
        if not p:
            s += "[]"
        else:
            n_face_up = count_face_up(p)
            for i in range(0, n_face_up):
                s += f"[{p[0]}]"
            for card in p[n_face_up:]:
                if xray:
                    s += f"[{card}]"
                else:
                    s += "[*]"
        s += "\t\t"
    print(s)


def count_face_up(pile):
    if not pile:  # if the pile is empty, return 0
        return 0
    count = 1
    for card in pile[1:]:  # for cards after the first
        if card != pile[0]:  # if this card doesn't match the top card, it's still face down
            break
        count += 1  # otherwise, add it to the face-up count
    return count


def counts_face_down(piles):
    return [len(piles[i]) - count_face_up(piles[i]) for i, p in enumerate(piles)]


def are_neighbors(a, b):
    # jokers
    if a == 0 or b == 0:
        return True

    # king-ace wraparound
    if (a == 13 and b == 1) or (b == 13 and a == 1):
        return True

    # regular values
    if abs(a-b) == 1:
        return True

    return False


def get_neighbors(card):
    # jokers
    if card == 0:
        return [x for x in range(0, 14)]

    # king-ace wraparound
    if card == 13:
        return [12, 1]
    if card == 1:
        return [2, 13]
    # regular values
    return [card+1, card-1]


def check_moves(piles, discards):
    for p in piles:
        for d in discards:
            if p and d and are_neighbors(d[0], p[0]):
                return True
    return False


def flatten(piles):
    return [x for xs in piles for x in xs]


def duplicates_in_list(some_list, ignore=None):
    seen = []
    for item in some_list:
        if item in seen and item not in ignore:
            return True
        seen.append(item)


def get_tops(piles):
    tops = [pile[0] if pile else -1 for pile in piles[1:]]
    return tops
