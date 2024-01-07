from card import Card
from card import WrongCardSuit, WrongCardValue, CardPlayedOnItself
from pytest import raises
from constants import SUITS, VALUES


def test_wrong_value():
    with raises(WrongCardValue):
        Card(1, "spades")


def test_wrong_suite():
    with raises(WrongCardSuit):
        Card(2, 3)
        Card(2, "spade")


def get_effect_name_kwargs(card: Card) -> tuple[str, dict]:
    return card.play_effect.func.__name__, card.play_effect.keywords


def test_card_effect_assign() -> None:
    card: Card = Card(2, "spades")
    effect = get_effect_name_kwargs(card)
    assert effect[0] == Card._draw_cards.__name__
    assert effect[1].get("number", None) == 2

    card = Card(3, "spades")
    effect = get_effect_name_kwargs(card)
    assert effect[0] == Card._draw_cards.__name__
    assert effect[1].get("number", None) == 3

    card = Card(4, "spades")
    assert get_effect_name_kwargs(card)[0] == Card._skip_next_player.__name__

    card = Card("king", "spades")
    effect = get_effect_name_kwargs(card)
    assert effect[0] == Card._king_draw_cards.__name__
    assert effect[1].get("previous", None) is True

    card = Card("king", "diamonds")
    assert get_effect_name_kwargs(card)[0] == Card._block_king.__name__

    card = Card("queen", "spades")
    assert get_effect_name_kwargs(card)[0] == Card._no_effect.__name__


def test_can_play_standard() -> None:
    center: Card = Card(9, "spades")
    played: Card = Card(9, "diamonds")
    game_state: dict = {}
    assert center.can_play(played, **game_state) is True

    played = Card(10, "spades")
    assert center.can_play(played, **game_state) is True


def test_can_play_queen() -> None:
    played: Card = Card("queen", "spades")
    center: Card = Card(2, "diamonds")
    game_state: dict = {}
    assert center.can_play(played, **game_state) is True

    played = Card("queen", "spades")
    for value, suit in zip(VALUES, SUITS):
        center = Card(value, suit)
        if center == played:
            with raises(CardPlayedOnItself):
                center.can_play(played, **game_state)
        else:
            assert center.can_play(played, **game_state) is True

    game_state = {"penalty": 2}
    assert center.can_play(played, **game_state) is False

    game_state = {"penalty": 5, "king": True}
    center = Card("king", "spades")
    assert center.can_play(played, **game_state) is False

    game_state = {"skip": 1}
    center = Card("4", "spades")
    assert center.can_play(played, **game_state) is False

    game_state = {"suit": ("diamonds", 1)}
    center = Card("ace", "spades")
    assert center.can_play(played, **game_state) is False

    game_state = {"value": ("9", 3)}
    center = Card("jack", "spades")
    assert center.can_play(played, **game_state) is False


def test_king() -> None:
    center: Card = Card("king", "spades")
    played: Card = Card(9, "spades")
    game_state: dict = {"king": True}

    assert center.can_play(played, **game_state) is False

    for suit in SUITS:
        played = Card("king", suit)
        if center == played:
            with raises(CardPlayedOnItself):
                center.can_play(played, **game_state)
        else:
            assert center.can_play(played, **game_state) is True

    played = Card(9, "spades")
    game_state = {}
    assert center.can_play(played, **game_state) is True


def test_can_play_four() -> None:
    center: Card = Card(4, "spades")
    played: Card = Card(4, "diamonds")
    game_state: dict = {"skip": 1}
    assert center.can_play(played, **game_state) is True

    played = Card(5, "spades")
    assert center.can_play(played, **game_state) is False


def test_can_play_req_value() -> None:
    center: Card = Card(7, "spades")
    played: Card = Card(7, "diamonds")
    game_state: dict = {"value": ("7", 1)}
    assert center.can_play(played, **game_state) is True

    played = Card(8, "spades")
    assert center.can_play(played, **game_state) is False


def test_can_play_req_suit() -> None:
    center: Card = Card("ace", "spades")
    played: Card = Card(9, "diamonds")
    game_state: dict = {"suit": ("diamonds", 1)}
    assert center.can_play(played, **game_state) is True

    played = Card(9, "hearts")
    assert center.can_play(played, **game_state) is False


def test_can_play_penalty() -> None:
    center: Card = Card(3, "spades")
    played: Card = Card(3, "diamonds")
    game_state: dict = {"penalty": 3}
    assert center.can_play(played, **game_state) is True

    played = Card(2, "spades")
    assert center.can_play(played, **game_state) is True

    played = Card(4, "spades")
    assert center.can_play(played, **game_state) is False
