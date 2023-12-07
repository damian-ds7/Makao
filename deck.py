from constants import VALUES, SYMBOLS
from card import Card
from random import shuffle


class Deck:
    def __init__(self):
        """
        Represents a deck of cards.
        """
        self._cards = [Card(value, symbol) for value in VALUES for symbol in SYMBOLS]

    @property
    def cards(self) -> list[Card]:
        return self._cards

    def __str__(self) -> str:
        return " ".join([str(card) for card in self.cards])

    def shuffle(self):
        shuffle(self.cards)

    def deal(self) -> Card:
        return self.cards.pop()


deck = Deck()
print(deck)
print()
deck.shuffle()
print(deck)
