from util import *


# A series of hands, at the end of which someone has no cards.
class Round:
    def __init__(self, player1, player2, halves, interactive=False):
        self.left_deck = player1.make_piles(halves[0], 5)
        self.right_deck = player2.make_piles(halves[1], 5)
        self.left_discard = []
        self.right_discard = []
        if interactive:
            print("*** Initializing Board ***")
            self.print_board(player1, player2, interactive=True)

    def print_board(self, player1, player2, xray=False, interactive=False):
        p1_piles = player1.piles
        p2_piles = player2.piles
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
        pprint_piles(p1_piles, xray=xray)
        print("\nPlayer 2")
        pprint_piles(p2_piles, xray=xray)
        if interactive:
            input()


    def play_hand(self, player1, player2, interactive=False):
        p1_piles = player1.piles
        p2_piles = player2.piles
        left_discard = self.left_discard
        right_discard = self.right_discard
        left_deck = self.left_deck
        right_deck = self.right_deck

        # Flip cards
        if left_deck:
            left_discard.insert(0, left_deck.pop(0))
        if right_deck:
            right_discard.insert(0, right_deck.pop(0))

        if interactive:
            print("\n"*50)
            print("*** Flipped new cards ***")
            self.print_board(player1, player2, interactive=True)

        # Race!
        while True:
            # See who can play
            p1_has_moves = check_moves(p1_piles, [left_discard, right_discard])
            p2_has_moves = check_moves(p2_piles, [left_discard, right_discard])

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
                left_discard, right_discard = self.play_card(player1, [left_discard, right_discard])
            else:
                left_discard, right_discard = self.play_card(player2, [left_discard, right_discard])

            if interactive:
                print("\n" * 50)
                print(f"*** {fastest_player} played a card ***")
                self.print_board(player1, player2, interactive=True)

            # If someone won with this play, stop!
            winner = Round.find_winner([player1, player2])
            if winner:
                break

    @staticmethod
    def play_card(player, discard_piles, verbose=False):
        play_on = None  # the discard pile to play a card on
        play_from = None  # the pile to play from

        order = player.round_strategy(player.piles)
        for i in order:
            if player.piles[i]:
                top = player.piles[i][0]
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
            pprint_piles(player.piles)
            print(discard_piles)
            print("Playing...")

        # Get the card to play
        card_to_play = player.piles[play_from].pop(0)

        # If it's a joker, declare it to be one of the neighboring cards, whichever would allow you to play again
        # FIXME: This differs from the IRL rules
        if card_to_play == 0:
            card_to_play = Round.choose_joker_value(player.piles, discard_piles)

        # Play the card
        discard_piles[play_on].insert(0, card_to_play)

        # adjust piles
        player.adjust_piles()

        if verbose:
            pprint_piles(player.piles)
            print(discard_piles)

        # return new discard piles
        return discard_piles[0], discard_piles[1]

    def play(self, player1, player2, verbose=True, interactive=False):
        player1.adjust_piles()
        player2.adjust_piles()
        if interactive:
            print("*** Adjusted Piles***")
            self.print_board(player1, player2, interactive=True)
        p1_piles = player1.piles
        p2_piles = player2.piles
        left_discard = self.left_discard
        right_discard = self.right_discard
        left_deck = self.left_deck
        right_deck = self.right_deck

        # Play hands until someone wins, or you run out of cards
        winner = None
        while not winner and (left_deck or right_deck):
            self.play_hand(player1, player2, interactive=interactive)
            winner = Round.find_winner([player1, player2])
        if not winner:
            pass  # TODO: handle a "tie" (i.e. running out of cards to flip before anyone wins)

        if verbose:
            if interactive:
                print("\n"*50)
            print(f"WINNER: Player {winner}")
            self.print_board(player1, player2, xray=True, interactive=interactive)

        return {"winner": winner, "player1": p1_piles, "player2": p2_piles,
                "left_deck": left_deck, "right_deck": right_deck,
                "left_discard": left_discard, "right_discard": right_discard}

    # Prioritize opening a second move, then turning over cards
    @staticmethod
    def prioritize_next_move(piles):
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


    @staticmethod
    def prioritize_revealing_cards(piles):
        # Put piles in order of most unturned cards
        pile_sizes = counts_face_down(piles)
        order = sorted(range(len(pile_sizes)), key=lambda k: pile_sizes[k], reverse=True)
        # Add joker at the end
        order.remove(0)
        order.append(0)
        return order


    @staticmethod
    def choose_joker_value(piles, discard_piles):
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


    @staticmethod
    def find_winner(players):
        for i, player in enumerate(players):
            piles = player.piles
            # If they have all empty piles, winner!
            if piles.count([]) == len(piles):
                return i + 1
        return None  # if both have cards, return None

