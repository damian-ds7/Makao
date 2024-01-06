from functools import partial
from constants import SUITS, VALUES
from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    from game import Game


class WrongCardValue(Exception):
    def __init__(
        self,
        value: Union[int, str],
        message: str = "Must be a string containing a number from 2 to 10 or one of four letters: J, Q, K, A",
    ) -> None:
        super().__init__(message, value)


class WrongCardSuit(Exception):
    def __init__(
        self,
        suit: str,
        message: str = "Must be a string containing one of four possible suits: clubs, spades, diamonds, hearts",
    ) -> None:
        super().__init__(message, suit)


class CardPlayedOnItself(Exception):
    def __init__(
        self,
        card: "Card",
        message: str = "Card cannot be played on itself",
    ) -> None:
        super().__init__(message, repr(card))


class Card:
    def __init__(self, value: Union[str, int], suit: str) -> None:
        """
        Represents a card from a deck of cards.

        :param value: card's value, from 2 to A
        :param suit: card's suit: clubs, spades, diamonds, hearts
        :raises WrongCardValue: Is raised if the value is not in the VALUES list
        :raises WrongCardSuit: Is raised if the suit is not in the SUITS list
        """
        value = str(value).lower()
        suit = str(suit).lower()
        if value not in VALUES:
            raise WrongCardValue(value)
        if suit not in SUITS:
            raise WrongCardSuit(suit)

        self._value: str = value
        self._suit: str = suit
        if value != "king":
            self._play_effect: Callable = self.EFFECT_MAP.get(
                self.value, partial(self._no_effect)
            )
        else:
            self._play_effect = self.KING_EFFECT_MAP.get(
                self.suit, partial(self._block_king)
            )

    @property
    def value(self) -> str:
        return self._value

    @property
    def suit(self) -> str:
        return self._suit

    @property
    def play_effect(self):
        return self._play_effect

    def get_image_name(self) -> str:
        return f"images/{self.suit}_{self.value}.png"

    def can_play(self, played_card: "Card", **kwargs) -> bool:
        """
        Checks if the card selected by the player can be played

        :param played_card: The card that is currently played

        :key req_suit: Tuple with required suit and number of turns it will stay
        :key req_value: Tuple with required value and number of turns it will stay
        :key four_played: True if four was played
        :key king_played: True if king was played
        :key jack_played: True if jack was played
        :key ace_played: True if ace was played
        :key penalty: Penalty value

        :raises CardPlayedOnItself: If two identical cards are compared

        :return: True if the selected card can be played, False otherwise
        """
        req_suit: tuple[str, int] = kwargs.get("suit", None)
        req_value: tuple[str, int] = kwargs.get("value", None)
        four_played: int = kwargs.get("skip", None)
        king_played: bool = kwargs.get("king", None)
        jack_played: bool = kwargs.get("jack", None)
        ace_played: bool = kwargs.get("ace", None)
        penalty: int = kwargs.get("penalty", None)

        if self == played_card:
            raise CardPlayedOnItself(self)

        conditions = [
            (four_played, lambda: played_card.value == "4"),
            (
                req_value,
                lambda: req_value[0] == played_card.value
                or played_card.value == "jack",
            ),
            (
                req_suit,
                lambda: req_suit[0] == played_card.suit or played_card.value == "ace",
            ),
            (
                jack_played,
                lambda: self.check_compatible(played_card)
                and played_card.value not in ["2", "3", "4", "jack"]
                and not (played_card.value == "king" and played_card.suit in ["spades", "hearts"])
            ),
            (
                ace_played,
                lambda: self.check_compatible(played_card)
                and played_card.value not in ["2", "3", "4", "jack"]
                and not (played_card.value == "king" and played_card.suit in ["spades", "hearts"])
            ),
            (
                penalty and not king_played,
                lambda: self.check_compatible(played_card)
                and played_card.value in ["2", "3"],
            ),
            (king_played, lambda: played_card.value == "king"),
            (self.value == "queen" or played_card.value == "queen", lambda: True),
        ]

        for condition, result in conditions:
            if condition:
                return result()

        return self.check_compatible(played_card)

    def check_compatible(self, played_card: "Card") -> bool:
        return self.value == played_card.value or self.suit == played_card.suit

    @staticmethod
    def _no_effect(game: "Game"):
        pass

    @staticmethod
    def _draw_cards(game: "Game", number: int) -> None:
        game._increase_penalty(number)

    @staticmethod
    def _skip_next_player(game: "Game") -> None:
        game._increment_skip()

    @staticmethod
    def _request_value(game: "Game") -> None:
        game._jack_played()

    @staticmethod
    def _king_draw_cards(game: "Game", previous: bool = False) -> None:
        game._king_played(previous=previous)

    @staticmethod
    def _block_king(game: "Game") -> None:
        game._reset_king()

    @staticmethod
    def _request_suit(game: "Game") -> None:
        game._ace_played()

    EFFECT_MAP: dict[str, Callable] = {
        "2": partial(_draw_cards, number=2),
        "3": partial(_draw_cards, number=3),
        "4": partial(_skip_next_player),
        "jack": partial(_request_value),
        "ace": partial(_request_suit),
    }

    KING_EFFECT_MAP: dict[str, Callable] = {
        "spades": partial(_king_draw_cards, previous=True),
        "hearts": partial(_king_draw_cards),
    }

    def __repr__(self) -> str:
        return f"Card('{self.value}', '{self.suit}')"

    def __eq__(self, card: object) -> bool:
        if not isinstance(card, Card):
            return NotImplemented
        return self.value == card.value and self.suit == card.suit
