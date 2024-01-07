from card import Card
from players import ComputerPlayer


def test_find_move_one_card():
    player = ComputerPlayer()
    player._hand = [Card("9", "spades")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [Card("9", "spades")]


def test_find_best_plays_multiple_cards():
    player = ComputerPlayer()
    player._hand = [Card("9", "spades"), Card("8", "spades"), Card("7", "hearts")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("9", "spades"),
        Card("8", "spades"),
    ]


def test_find_best_plays_no_playable_cards():
    player = ComputerPlayer()
    player._hand = [Card("9", "hearts"), Card("8", "hearts")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == []


def test_find_best_plays_special_card():
    player = ComputerPlayer()
    player._hand = [Card("2", "spades"), Card("8", "spades")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("8", "spades"),
        Card("2", "spades"),
    ]


def test_find_best_plays_ace_card():
    player = ComputerPlayer()
    player._hand = [Card("ace", "spades"), Card("8", "spades")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("ace", "spades"),
        Card("8", "spades"),
    ]


def test_find_best_plays_jack_and_ace():
    player = ComputerPlayer()
    player._hand = [Card("jack", "spades"), Card("ace", "spades"), Card("8", "spades")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("jack", "spades"),
        Card("8", "spades"),
    ]


def test_find_best_plays_king_spades_or_hearts():
    player = ComputerPlayer()
    player._hand = [Card("king", "spades"), Card("king", "hearts"), Card("8", "spades")]
    center = Card("king", "diamonds")
    params = {"center": center}
    assert player.find_best_plays(**params) == [Card("king", "hearts")]


def test_find_best_plays_king_spades_or_hearts_previous_player_less_cards():
    player = ComputerPlayer()
    player._hand = [Card("king", "spades"), Card("king", "hearts"), Card("8", "spades")]
    center = Card("king", "diamonds")
    params = {"center": center, "prev_len": 3, "next_len": 4}
    assert player.find_best_plays(**params) == [Card("king", "spades")]


def test_find_best_plays_king_spades():
    player = ComputerPlayer()
    player._hand = [Card("king", "spades"), Card("8", "spades")]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("8", "spades"),
        Card("king", "spades"),
    ]


def test_find_best_plays_multiple_special_cards():
    player = ComputerPlayer()
    player._hand = [
        Card("2", "spades"),
        Card("4", "spades"),
        Card("8", "spades"),
    ]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("8", "spades"),
        Card("2", "spades"),
    ]


def test_find_best_plays_no_special_cards():
    player = ComputerPlayer()
    player._hand = [Card("9", "spades"), Card("8", "hearts"), Card("7", "diamonds")]
    center = Card("6", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("9", "spades"),
    ]


def test_find_best_plays_chained_normal_and_draw():
    player = ComputerPlayer()
    player._hand = [
        Card("2", "spades"),
        Card("7", "diamonds"),
        Card("7", "clubs"),
        Card("8", "clubs"),
        Card("10", "clubs"),
    ]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("7", "diamonds"),
        Card("7", "clubs"),
        Card("8", "clubs"),
        Card("10", "clubs"),
    ]


def test_find_best_plays_chained_normal_and_chained_draw():
    player = ComputerPlayer()
    player._hand = [
        Card("2", "spades"),
        Card("3", "spades"),
        Card("7", "diamonds"),
        Card("7", "clubs"),
        Card("8", "clubs"),
        Card("10", "clubs"),
    ]
    center = Card("7", "spades")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("2", "spades"),
        Card("3", "spades"),
    ]


def test_find_best_plays_king_played():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "diamonds"),
        Card("king", "spades"),
        Card("3", "hearts"),
        Card("2", "hearts"),
    ]
    center = Card("king", "hearts")
    params = {"center": center, "king": True, "penalty": 5}
    assert player.find_best_plays(**params) == [
        Card("king", "spades"),
    ]


def test_find_best_plays_king_played_2():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "diamonds"),
        Card("3", "spades"),
        Card("2", "spades"),
    ]
    center = Card("king", "spades")
    params = {"center": center, "king": True, "penalty": 5}
    assert player.find_best_plays(**params) == [
        Card("king", "diamonds"),
    ]


def test_find_best_plays_king_played_3():
    player = ComputerPlayer()
    player._hand = [Card("3", "hearts"), Card("2", "hearts"), Card("7", "hearts")]
    center = Card("king", "spades")
    params = {"center": center, "king": True, "penalty": 5}
    assert player.find_best_plays(**params) == []


def test_find_best_plays_four_played():
    player = ComputerPlayer()
    player._hand = [Card("4", "hearts"), Card("2", "hearts"), Card("7", "hearts")]
    center = Card("4", "spades")
    params = {"center": center, "skip": 1}
    assert player.find_best_plays(**params) == [
        Card("4", "hearts"),
    ]


def test_find_best_plays_four_played_chained():
    player = ComputerPlayer()
    player._hand = [Card("4", "hearts"), Card("4", "clubs"), Card("7", "hearts")]
    center = Card("4", "spades")
    params = {"center": center, "skip": 1}
    assert player.find_best_plays(**params) == [
        Card("4", "hearts"),
        Card("4", "clubs")
    ]


def test_find_best_plays_four_played_none():
    player = ComputerPlayer()
    player._hand = [
        Card("3", "hearts"),
        Card("2", "hearts"),
        Card("7", "hearts")
    ]
    center = Card("4", "spades")
    params = {"center": center, "skip": 1}
    assert player.find_best_plays(**params) == []


def test_find_best_plays_draw_played():
    player = ComputerPlayer()
    player._hand = [
        Card("3", "hearts"),
        Card("2", "hearts"),
        Card("7", "hearts")
    ]
    center = Card("2", "spades")
    params = {"center": center, "penalty": 1}
    assert player.find_best_plays(**params) == [
        Card("2", "hearts"),
        Card("3", "hearts"),
    ]


def test_find_best_plays_draw_played_none():
    player = ComputerPlayer()
    player._hand = [
        Card("7", "hearts")
    ]
    center = Card("2", "spades")
    params = {"center": center, "penalty": 1}
    assert player.find_best_plays(**params) == []


def test_find_best_plays_draw_played_king_in_deck():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "hearts"),
        Card("7", "hearts")
    ]
    center = Card("2", "hearts")
    params = {"center": center, "penalty": 1}
    assert player.find_best_plays(**params) == []


def test_find_best_plays_req_suit():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "spades"),
        Card("7", "hearts")
    ]
    center = Card("ace", "clubs")
    params = {"center": center, "suit": ("hearts", 1)}
    assert player.find_best_plays(**params) == [Card("7", "hearts")]


def test_find_best_plays_req_suit_chained():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "spades"),
        Card("7", "hearts"),
        Card("7", "spades"),
    ]
    center = Card("ace", "clubs")
    params = {"center": center, "suit": ("hearts", 1)}
    assert player.find_best_plays(**params) == [
        Card("7", "hearts"),
        Card("7", "spades"),
        Card("king", "spades"),
    ]


def test_find_best_plays_req_val():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "spades"),
        Card("7", "hearts"),
        Card("8", "hearts")
    ]
    center = Card("jack", "clubs")
    params = {"center": center, "value": ("7", 1)}
    assert player.find_best_plays(**params) == [Card("7", "hearts")]


def test_find_best_plays_queen_1():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "spades"),
        Card("queen", "clubs"),
        Card("8", "hearts")
    ]
    center = Card("jack", "hearts")
    params = {"center": center}
    assert player.find_best_plays(**params) == [
        Card("8", "hearts"),
        Card("queen", "clubs"),
        Card("king", "spades"),
    ]


def test_find_best_plays_queen_2():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "spades"),
        Card("queen", "clubs"),
    ]
    center = Card("ace", "hearts")
    params = {"center": center, "suit": ("hearts", 1)}
    assert player.find_best_plays(**params) == []


def test_find_best_plays_queen_3():
    player = ComputerPlayer()
    player._hand = [
        Card("king", "spades"),
        Card("queen", "clubs"),
    ]
    center = Card("jack", "hearts")
    params = {"center": center, "value": ("7", 1)}
    assert player.find_best_plays(**params) == []
