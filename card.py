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
            self._play_effect: Callable = self.EFFECT_MAP.get(self.value, self._no_effect)
        else:
            self._play_effect = self.KING_EFFECT_MAP.get(self.suit, self._block_king)

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
        Checks if the card selected by the player can be played.

        :param played_card: The card that is currently played.
        :return: True if the selected card can be played, False otherwise.
        """
        req_suit: tuple[str, int] = kwargs.get("suit", None)
        req_value: tuple[str, int] = kwargs.get("value", None)
        four_played: int = kwargs.get("skip", None)
        king_played: bool = kwargs.get("king", None)
        penalty: int = kwargs.get("penalty", None)

        # if self.value == "4" and played_card.value == "4":
        #     return True
        if four_played:
            return played_card.value == "4"
        elif req_value:
            return req_value[0] == played_card.value
        elif req_suit:
            return req_suit[0] == played_card.suit
        elif penalty and not king_played:
            return self.check_compatible(played_card) and played_card.value in ["2", "3"]
        elif king_played:
            return played_card.value == "king"
        elif self.value == "queen" or played_card.value == "queen":
            return True

        return self.check_compatible(played_card)

    def check_compatible(self, played_card: "Card") -> bool:
        return self.value == played_card.value or self.suit == played_card.suit

    @staticmethod
    def _no_effect(game: "Game"):
        pass

    @staticmethod
    def _draw_cards(game: "Game", number: int) -> None:
        game.increase_penalty(number)

    @staticmethod
    def _skip_next_player(game: "Game") -> None:
        game.increment_skip()

    @staticmethod
    def _request_value(game: "Game") -> None:
        game.jack_played()

    @staticmethod
    def _king_draw_cards(game: "Game", previous: bool = False) -> None:
        game.king_played(previous=previous)

    @staticmethod
    def _block_king(game: "Game") -> None:
        game.reset_king()

    @staticmethod
    def _request_suit(game: "Game") -> None:
        game.ace_played()

    EFFECT_MAP: dict[str, Callable] = {
        "2": partial(_draw_cards, number=2),
        "3": partial(_draw_cards, number=3),
        "4": _skip_next_player,
        "jack": _request_value,
        "ace": _request_suit,
    }

    KING_EFFECT_MAP: dict[str, Callable] = {
        "spades": partial(_king_draw_cards, previous=True),
        "hearts": _king_draw_cards,
    }

    def __repr__(self) -> str:
        return f"Card('{self.value}', '{self.suit}')"

    def __eq__(self, card: object) -> bool:
        if not isinstance(card, Card):
            return NotImplemented
        return self.value == card.value and self.suit == card.suit
