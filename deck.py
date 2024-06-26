from constants import VALUES, SUITS
from card import Card
from random import shuffle


class CardAlreadyInDeckError(Exception):
    def __init__(
        self,
        card: Card,
        message: str = "Given card is already present in deck",
    ) -> None:
        super().__init__(message, repr(card))


class DeckAlreadyEmptyError(IndexError):
    def __init__(
        self,
        message: str = "The deck is already empty, cannot draw card",
    ) -> None:
        super().__init__(message)


class Deck:
    def __init__(self, empty: bool = False, shuffle: bool = True):
        """
        Class representing a deck of cards
        """
        self._deck: list[Card] = (
            []
            if empty
            else [Card(value, suit) for value in VALUES for suit in SUITS]
        )
        if shuffle:
            self.shuffle_deck()

    @property
    def deck(self) -> list[Card]:
        return self._deck

    def __str__(self) -> str:
        return " ".join([str(card) for card in self.deck])

    def add_card(self, card: Card):
        if card in self.deck:
            raise CardAlreadyInDeckError(card)
        self.deck.append(card)

    def shuffle_deck(self) -> None:
        shuffle(self.deck)

    def deal(self) -> Card:
        try:
            return self.deck.pop()
        except IndexError:
            raise DeckAlreadyEmptyError

    def __len__(self) -> int:
        return len(self.deck)
