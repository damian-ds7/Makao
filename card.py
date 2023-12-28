from constants import SYMBOLS, VALUES
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


class WrongCardSymbol(Exception):
    def __init__(
        self,
        symbol: str,
        message: str = "Must be a string containing one of four possible symbols: clubs, spades, diamonds, hearts",
    ) -> None:
        super().__init__(message, symbol)


class Card:
    def __init__(self, value: Union[str, int], symbol: str) -> None:
        """
        Represents a card from a deck of cards.

        :param value: card's value, from 2 to A
        :type value: str
        :param symbol: card's symbol: clubs, spades, diamonds, hearts
        :type symbol: str
        :raises WrongCardValue: Is raised if the value is not in the VALUES list
        :raises WrongCardSymbol: Is raised if the symbol is not in the SYMBOLS list
        """
        value = str(value)
        if value not in VALUES:
            raise WrongCardValue(value)
        if symbol not in SYMBOLS:
            raise WrongCardSymbol(symbol)

        self._value: str = value
        self._symbol: str = symbol
        effect_map: dict[str, Callable] = {
            "2": self._draw_cards,
            "3": self._draw_cards,
            "4": self._skip_next_player,
            "jack": self._request_value,
            "queen": self._play_any_card,
            "king": self._king_draw_cards,
            "ace": self._request_symbol,
        }
        self._play_effect: Callable = effect_map.get(self.value, self._no_effect)

    @property
    def value(self) -> str:
        return self._value

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def play_effect(self):
        return self._play_effect

    def get_image_name(self) -> str:
        return f"images/{self.symbol}_{self.value}.png"

    def can_play(self, played_card: "Card") -> bool:
        """
        Checks if card selected by the player can be played
        """
        return self.symbol == played_card.symbol or self.value == played_card.value

    def _no_effect(self, game: "Game"):
        pass

    def _draw_cards(self, game: "Game"):
        number = int(self.value)
        game.increase_penalty(number)

    def _skip_next_player(self, game: "Game"):
        pass

    def _request_value(self, game: "Game"):
        pass

    def _play_any_card(self, game: "Game"):
        pass

    def _king_draw_cards(self, game: "Game"):
        pass

    def _request_symbol(self, game: "Game"):
        game.select_symbol()

    def __repr__(self) -> str:
        return f"Card('{self.value}', '{self.symbol}')"

    def __eq__(self, card: object) -> bool:
        if not isinstance(card, Card):
            return NotImplemented
        return self.value == card.value and self.symbol == card.symbol
