from constants import SYMBOLS, VALUES
from typing import Union


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

        self._value = value
        self._symbol = symbol

    @property
    def value(self) -> str:
        return self._value

    @property
    def symbol(self) -> str:
        return self._symbol

    def get_image_name(self) -> str:
        return f"images/{self.symbol}_{self.value}.png"

    def can_play(self, played_card: "Card") -> bool:
        """
        Checks if card selected by the player can be played
        """
        return True

    def __repr__(self) -> str:
        return f"Card('{self.value}', '{self.symbol}')"

    def __eq__(self, card: object) -> bool:
        if not isinstance(card, Card):
            return NotImplemented
        return self.value == card.value and self.symbol == card.symbol
