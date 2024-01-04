from card import Card
from card import WrongCardSuit, WrongCardValue
from pytest import raises


def test_wrong_value():
    with raises(WrongCardValue):
        Card(1, "spades")


def test_wrong_suite():
    with raises(WrongCardSuit):
        Card(2, 3)
        Card(2, "spade")


def get_effect_name_kwargs(card: Card) -> tuple[str, dict]:
    return card.play_effect.func.__name__, card.play_effect.keywords


def test_card_effect_assign():
    card: Card = Card(2, "spades")
    assert get_effect_name_kwargs(card)[0] == Card._draw_cards.__name__

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


def test_can_play_standard():
    center: Card = Card(9, "spades")
    played: Card = Card(9, "diamonds")
    game_state: dict = {}
    assert center.can_play(played, **game_state) is True

    played = Card(10, "spades")
    assert center.can_play(played, **game_state) is True


def test_can_play_queen():
    center: Card = Card("queen", "spades")
    played: Card = Card(9, "diamonds")
    game_state: dict = {}
    assert center.can_play(played, **game_state) is True

    center = Card(2, "hearts")
    played = Card("queen", "spades")
    assert center.can_play(played, **game_state) is True
