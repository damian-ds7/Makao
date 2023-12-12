from card import Card
from card import WrongCardSymbol, WrongCardValue
from pytest import raises


def test_card_value():
    card = Card("2", "clubs")
    assert card.value == "2"


def test_card_value_int():
    card = Card(2, "clubs")
    assert card.value == "2"


def test_card_symbol_str():
    card = Card("A", "hearts")
    assert card.symbol_str == "hearts"
    assert card.value == "A"


def test_card_symbol():
    card = Card("Q", "spades")
    assert card.symbol == "\u2660"


def test_card_color():
    card = Card("7", "diamonds")
    assert card.color == "red"


def test_card_str():
    card = Card("10", "clubs")
    assert str(card) == "\033[97m10\u2663\033[0m"


def test_card_repr():
    card = Card("J", "hearts")
    assert repr(card) == "Card('J', 'hearts')"


def test_wrong_card_value():
    with raises(WrongCardValue):
        Card("15", "clubs")


def test_wrong_card_symbol():
    with raises(WrongCardSymbol):
        Card("5", "stars")


def test_card_value_property():
    card = Card("9", "spades")
    assert card.value == "9"


def test_card_symbol_property():
    card = Card("K", "diamonds")
    assert card.symbol == "\u2666"
