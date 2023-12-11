from constants import SYMBOLS, SYMBOLS_UTF_VAL, SYMBOLS_COLORS, VALUES


class WrongCardValue(Exception):
    def __init__(
        self,
        value,
        message="Must be a string containing a number from 2 to 10 or one of four letters: J, Q, K, A",
    ) -> None:
        super().__init__(message, value)


class WrongCardSymbol(Exception):
    def __init__(
        self,
        symbol,
        message="Must be a string containing one of four possible symbols: clubs, spades, diamonds, hearts",
    ) -> None:
        super().__init__(message, symbol)


class Card:
    def __init__(self, value: str, symbol: str) -> None:
        """
        Represents a card from a deck of cards.

        :param value: card's value, from 2 to A
        :type value: str
        :param symbol: card's symbol: clubs, spades, diamonds, hearts
        :type symbol: str
        :raises WrongCardValue: Is raised if the value is not in the VALUES list
        :raises WrongCardSymbol: Is raised if the symbol is not in the SYMBOLS list
        """
        if value not in VALUES:
            raise WrongCardValue(value)
        if symbol not in SYMBOLS:
            raise WrongCardSymbol(symbol)

        self._value = value
        self._symbol_str = symbol
        self._symbol = SYMBOLS_UTF_VAL[symbol]
        self._color = SYMBOLS_COLORS[symbol]

    @property
    def value(self) -> str:
        return self._value

    @property
    def symbol_str(self) -> str:
        return self._symbol_str

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def color(self) -> str:
        return self._color

    def __str__(self):
        reset_color = "\033[0m"
        return f"{self.color}{self.value}{self.symbol}{reset_color}"

    def __repr__(self) -> str:
        return f"Card('{self.value}', '{self.symbol_str}')"
