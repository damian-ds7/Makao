from card import Card
from deck import Deck
from deck import CardAlreadyInDeckError, DeckAlreadyEmptyError
from pytest import raises
from constants import VALUES, SUITS


def test_take_from_empty():
    deck = Deck(empty=True)
    with raises(DeckAlreadyEmptyError):
        deck.deal()


def test_card_already_in_deck():
    deck = Deck()
    card = Card("2", "spades")
    with raises(CardAlreadyInDeckError):
        deck.add_card(card)


def test_empty_deck():
    deck = Deck(empty=True)
    assert len(deck) == 0


def test_full_deck():
    deck = Deck(empty=True)
    assert len(deck) == 52


def test_shuffle(monkeypatch):
    def mock_shuffle_deck(self):
        self._deck.reverse()

    monkeypatch.setattr(Deck, "shuffle_deck", mock_shuffle_deck)

    deck = Deck()
    assert deck.deal() == Card(VALUES[0], SUITS[0])
