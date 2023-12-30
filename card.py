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
        if value != "king" or symbol in ["diamonds", "clubs"]:
            effect_map: dict[str, Callable] = {
                "2": self._draw_cards,
                "3": self._draw_cards,
                "4": self._skip_next_player,
                "jack": self._request_value,
                "queen": self._play_any_card,
                "ace": self._request_symbol,
            }
            self._play_effect: Callable = effect_map.get(self.value, self._no_effect)
        else:
            effect_map = {
                # "hearts": NotImplemented,
                # "spades": NotImplemented
            }
            self._play_effect = effect_map.get(self.value, self._no_effect)

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

    def can_play(self, played_card, **kwargs) -> bool:
        """
        Checks if the card selected by the player can be played.

        :param played_card: The card that is currently played.
        :return: True if the selected card can be played, False otherwise.
        """
        req_symbol: str = kwargs.get("symbol", None)
        req_value: str = kwargs.get("value", None)
        four_played: bool = kwargs.get("four", None)

        if self.value == "4" and played_card.value == "4":
            return True
        if req_value and req_value == played_card.value:
            return True
        if req_symbol and req_symbol == played_card.symbol:
            return True
        if four_played and played_card.value == "4":
            return True

        return self.symbol == played_card.symbol or self.value == played_card.value

    def _no_effect(self, game: "Game"):
        pass

    def _draw_cards(self, game: "Game") -> None:
        number = int(self.value)
        game.increase_penalty(number)

    def _skip_next_player(self, game: "Game") -> None:
        game.increment_skip()

    def _request_value(self, game: "Game") -> None:
        game.selection(VALUES[3:9])

    def _play_any_card(self, game: "Game") -> None:
        pass

    def _king_draw_cards(self, game: "Game") -> None:
        pass

    def _request_symbol(self, game: "Game") -> None:
        game.selection(SYMBOLS)

    def __repr__(self) -> str:
        return f"Card('{self.value}', '{self.symbol}')"

    def __eq__(self, card: object) -> bool:
        if not isinstance(card, Card):
            return NotImplemented
        return self.value == card.value and self.symbol == card.symbol
