from typing import Generator, Any
from deck import Deck
from card import Card
from random import randint


class PlayNotAllowedError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class HumanPlayer:
    def __init__(self) -> None:
        """
        Class representing human player with a deck of cards rank and makao status
        """
        self._hand: list[Card] = []
        self.finished: bool = False
        self._makao_status: bool = False
        self._cards_played: int = 0
        self._drew_card: bool = False
        self._drew_penalty: bool = False
        self._skip_turns: int = 0
        self._penalty: bool = False
        self._played_king: bool = False

    @property
    def makao_status(self) -> bool:
        return self._makao_status

    @property
    def finished(self) -> bool:
        return self._finished

    @finished.setter
    def finished(self, finished: bool) -> None:
        self._finished = finished

    @property
    def drew_card(self) -> bool:
        """
        Returns True if player has drawn penalty
        """
        return self._drew_card

    @property
    def drew_penalty(self) -> bool:
        """
        Returns True if player has played at least one car
        """
        return self._drew_penalty

    @property
    def cards_played(self) -> int:
        """
        Returns current amount of cards played in one turn
        """
        return self._cards_played

    def reset_cards_played(self) -> None:
        self._cards_played = 0

    @property
    def penalty(self) -> bool:
        """
        Returns True if player is currently drawing penalty
        """
        return self._penalty

    @penalty.setter
    def penalty(self, new_penalty: bool) -> None:
        self._penalty = new_penalty

    @property
    def played_king(self) -> bool:
        return self._played_king

    @played_king.setter
    def played_king(self, new_val: bool) -> None:
        self._played_king = new_val

    def reset_turn_status(self):
        self._drew_card = False
        self._cards_played = 0
        self._drew_penalty = False

    def check_moved(self) -> bool:
        return self.drew_card or bool(self.cards_played) or self.drew_penalty

    @property
    def skip_turns(self) -> int:
        return self._skip_turns

    @skip_turns.setter
    def skip_turns(self, new_val) -> None:
        self._skip_turns = new_val

    @property
    def hand(self) -> list[Card]:
        return self._hand

    def draw_card(self, deck: Deck) -> None:
        if self.penalty:
            self._drew_penalty = True
            self._hand.append(deck.deal())
        elif not self.drew_card and not self.cards_played:
            self._hand.append(deck.deal())
            self._drew_card = True

    def play_card(self, card: Card) -> None:
        if (
            self.drew_card and card is self.hand[-1] and not self.cards_played
        ) or not self.drew_card:
            self.hand.remove(card)
            self._cards_played += 1
        else:
            raise PlayNotAllowedError("You cannot play this card")

    def makao_set_reset(self, say: bool = False) -> None:
        if say:
            self._makao_status = True
            return
        self._makao_status = False

    def player_info(self, human_computer: str = "Human player") -> tuple:
        cards: str = " ".join([str(card) for card in self.hand])
        return (
            f"{human_computer}",
            f"  Deck: {cards}",
            f"  Makao: {self.makao_status}",
        )

    def __str__(self) -> str:
        return " ".join([str(card) for card in self.hand])


class ComputerPlayer(HumanPlayer):
    # TODO:
    # - algorithm to choose best moves
    def __init__(self) -> None:
        """
        Class representing computer player with a deck of cards rank and makao status
        """
        super().__init__()

    def player_info(self, human_computer: str = "Computer player") -> tuple:
        return super().player_info(human_computer)

    def selection(self, items: list[str]) -> int:
        if len(items) == 4:
            return self.suit_select()
        else:
            return self.val_select(items)

    def suit_select(self) -> int:
        """
        Randomly selects a suit for the next player

        :return: The index of the selected suit
        """
        return randint(0, 3)

    def val_select(self, items: list[str]) -> int:
        """
        Calculates the value to select based on the player's hand

        :param items: list of values
        :return: Index of selected value or index of None in selection menu
        """
        values: list[str] = items[:-1]
        hand_values: list[str] = [card.value for card in self.hand]
        num_of_occurrences: list[int] = [hand_values.count(value) for value in values]
        return len(values) if not max(num_of_occurrences) else max(num_of_occurrences)

    def find_best_plays(self, **game_state) -> list[Card]:
        """
        Finds the best plays based on the given game parameters and player data

        :key players: A list of players in the game
        :key center: Current center card
        :key prev_len: Length of the previous player's deck
        :key next_len: Length of the next player's deck

        :return: Moves for computer to play.
        """
        game_params: dict[str, Any] = game_state
        self.previous_len: int = game_state.get("prev_len", 0)
        self.next_len: int = game_state.get("next_len", 0)
        possible_first_moves: list[Card] = self._get_possible_moves(**game_params)
        possible_movesets: list[tuple[str, list[Card]]] = self._get_movesets(
            possible_first_moves, **game_state
        )

        if len(possible_movesets) == 1 and possible_movesets[0][0] == "end":
            return possible_movesets[0][1]

        best_moves: list[Card] = (
            []
            if not possible_movesets
            else min(
                possible_movesets,
                key=lambda moveset: self.move_sort_key(moveset[0], len(moveset[1])),
            )[1]
        )
        return best_moves

    @staticmethod
    def _get_move_descriptor(moveset: list[Card]) -> str:
        """
        Get the move descriptor for a given card

        :param card: The card for which to get the move descriptor
        :return: Description of card's effect on the game
        """
        descriptors: dict[str, str] = {
            "2": "next_draw",
            "3": "next_draw",
            "4": "skip",
            "jack": "value_req",
            "ace": "suit_req",
        }
        king_descriptors: dict[str, str] = {
            "spades": "king_prev_draw",
            "hearts": "king_next_draw",
        }
        card = moveset[-1]
        val: str = card.value
        suit: str = card.suit
        descriptor = (
            descriptors.get(val, "normal")
            if val != "king"
            else king_descriptors.get(suit, "normal")
        )

        value = next(
            (card.value for card in moveset if card.value in ["jack", "ace"]), None
        )
        if descriptor == "normal" and value is not None:
            descriptor = descriptors[value]
        return descriptor

    def _get_possible_moves(self, **game_params) -> list[Card]:
        """
        Returns a list of possible first moves for the player

        :key center_card: center card
        :return: list of possible moves
        """
        center_card: Card = game_params.get("center", None)
        possible_moves: list[Card] = []
        for card in self.hand:
            if center_card.can_play(card, **game_params):
                possible_moves.append(card)
        return possible_moves

    @staticmethod
    def _simulate_params(first_move: Card, **game_params) -> dict[str, Any]:
        """
        Simulates the parameters for a game based on the first move card

        :param first_move: The first move card
        :return: A dictionary containing the simulated game parameters
        """
        new_params: dict[str, Any] = {}
        val: str = first_move.value
        suit: str = first_move.suit
        if val in ["2", "3"]:
            new_params.update({"penalty": int(first_move.value)})
        elif val == "4":
            new_params.update({"skip": 1})
        elif val == "king" and suit in ["spades", "hearts"]:
            new_params.update({"king": True})
        elif val == "ace":
            new_params.update({"ace": True})
        elif val == "jack":
            new_params.update({"jack": True})

        if "king" in game_params:
            new_params.update({"king": True})
        if "value" in game_params:
            new_params.update({"value": game_params["value"]})
        if "suit" in game_params:
            new_params.update({"suit": game_params["suit"]})

        return new_params

    @staticmethod
    def check_card_play_conditions(
        current_card: Card, card: Card, moveset: list[Card], **game_params
    ) -> bool:
        jack_ace_duplicate: bool = False
        if "jack" in game_params or "ace" in game_params and card.value in ["jack", "ace"]:
            jack_ace_duplicate = True
        return (
            card not in moveset
            and card != current_card
            and current_card.can_play(card)
            and not jack_ace_duplicate
        )

    def _generate_permutations(
        self, moveset: list[Card] = [], **game_params
    ) -> Generator[list[Card], None, None]:
        """
        Generates all possible permutations of movesets based on the current moveset and available cards.

        :param moveset: List of already added moves, last item is the last played card
        :param **game_params: Additional keyword arguments used to create simulated_params dict.
        :return: A generator that yields possible movesets
        """
        current_card: Card = moveset[-1]
        params: dict[str, Any] = self._simulate_params(current_card, **game_params)
        cards = list(
            filter(
                lambda card: self.check_card_play_conditions(
                    current_card, card, moveset, **params
                ),
                self.hand,
            )
        )
        if not cards or (
            current_card.value == "king" and current_card.suit in ["spades", "hearts"]
        ) or len(moveset) == 7:
            yield moveset
        else:
            for i, next_card in enumerate(cards):
                if current_card.can_play(next_card):
                    yield from self._generate_permutations(
                        moveset + [next_card], **game_params
                    )

    def _get_movesets(
        self, first_moves: list[Card], **game_params
    ) -> list[tuple[str, list[Card]]]:
        """
        Get the possible movesets based on the first moves and other optional arguments.

        :param first_moves: The list of first moves player can make
        :param **game_params: Optional keyword arguments passed to
                         _generate_permutations to simulate game_params

        :return: The list of possible movesets, where each moveset is represented as a tuple
            containing a descriptor string and a list of cards

        """
        possible_movesets: list[tuple[str, list[Card]]] = []
        for first_move in first_moves:
            moves: list[Card] = [first_move]
            for permutation in self._generate_permutations(moves, **game_params):
                if len(permutation) <= 4 and len(permutation) == len(self.hand):
                    return [("end", permutation)]
                descriptor: str = self._get_move_descriptor(permutation)
                if len(permutation) == len(self.hand) and len(permutation) > 4:
                    possible_movesets.append(
                        (descriptor, permutation[: len(permutation) - 1])
                    )
                else:
                    possible_movesets.append((descriptor, permutation))

        return possible_movesets

    def move_sort_key(self, descriptor: str, moveset_len: int):
        """
        Sorts the movesets based on their importance.

        :param descriptor: The descriptor for the moveset.
        :return: The importance of the moveset.
                 The smaller it is the more importan move is
        """
        movesets_importance: dict[str, int] = {
            "king_next_draw": 1,
            "next_draw": 2,
            "king_prev_draw": 3,
            "value_req": 4,
            "suit_req": 4,
            "skip": 4,
            "normal": 5,
        }

        if self.previous_len < self.next_len:
            (
                movesets_importance["king_next_draw"],
                movesets_importance["king_prev_draw"],
            ) = (
                movesets_importance["king_prev_draw"],
                movesets_importance["king_next_draw"],
            )

        if self.previous_len <= len(self.hand):
            movesets_importance["skip"] = movesets_importance["next_draw"]

        movesets_importance[descriptor] -= moveset_len

        return movesets_importance[descriptor]
