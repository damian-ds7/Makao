from typing import Optional, Union
from deck import Deck
from card import Card


class PlayNotAllowedError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class HumanPlayer:
    def __init__(self) -> None:
        """
        Class representing human player with a deck of cards rank and makao status
        """
        self._hand: list[Card] = []
        self._rank: Optional[int] = None
        self._makao_status: bool = False
        self._cards_played: int = 0
        self._drew_card: bool = False
        self._drew_penalty: bool = False
        self._skip_turns: int = 0
        self._penalty: bool = False
        self._played_king: bool = False

    @property
    def makao_status(self) -> bool:
        return self._makao_status

    @property
    def rank(self) -> Optional[int]:
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        self._rank = rank

    @property
    def drew_card(self) -> bool:
        """
        Returns True if player has drawn penalty
        """
        return self._drew_card

    @property
    def drew_penalty(self) -> bool:
        """
        Returns True if player has played at least one car
        """
        return self._drew_penalty

    @property
    def cards_played(self) -> int:
        """
        Returns current amount of cards played in one turn
        """
        return self._cards_played

    def reset_cards_played(self) -> None:
        self._cards_played = 0

    @property
    def penalty(self) -> bool:
        """
        Returns True if player is currently drawing penalty
        """
        return self._penalty

    @penalty.setter
    def penalty(self, new_penalty: bool) -> None:
        self._penalty = new_penalty

    @property
    def played_king(self) -> bool:
        return self._played_king

    @played_king.setter
    def played_king(self, new_val: bool) -> None:
        self._played_king = new_val

    def reset_turn_status(self):
        self._drew_card = False
        self._cards_played = 0
        self._drew_penalty = False

    def check_moved(self) -> bool:
        return self.drew_card or bool(self.cards_played) or self.drew_penalty

    @property
    def skip_turns(self) -> int:
        return self._skip_turns

    @skip_turns.setter
    def skip_turns(self, new_val) -> None:
        self._skip_turns = new_val

    @property
    def hand(self) -> list[Card]:
        return self._hand

    def draw_card(self, deck: Deck) -> None:
        if self.penalty:
            self._drew_penalty = True
            self._hand.append(deck.deal())
        elif not self.drew_card and not self.cards_played:
            self._hand.append(deck.deal())
            self._drew_card = True

    def play_card(self, card: Card) -> None:
        if (self.drew_card and card is self.hand[-1] and not self.cards_played) or not self.drew_card:
            self.hand.remove(card)
            self._cards_played += 1
        else:
            raise PlayNotAllowedError("You cannot play this card")

    def makao_set_reset(self, say: bool = False) -> None:
        if say:
            self._makao_status = True
            return
        self._makao_status = False

    def player_info(self, human_computer: str = "Human player") -> tuple:
        cards: str = " ".join([str(card) for card in self.hand])
        return (
            f"{human_computer}",
            f"  Deck: {cards}",
            f"  Makao: {self.makao_status}",
            f"  Rank: {self.rank}",
        )

    def __str__(self) -> str:
        return " ".join([str(card) for card in self.hand])


class ComputerPlayer(HumanPlayer):
    # TODO:
    # - algorithm to choose best moves
    def __init__(self) -> None:
        """
        Class representing computer player with a deck of cards rank and makao status
        """
        super().__init__()

    def player_info(self, human_computer: str = "Computer player") -> tuple:
        return super().player_info(human_computer)

    def find_best_play(self, **kwargs) -> Optional[Card]:
        center_card: Card = kwargs.get("center", None)
        players: list[Union[HumanPlayer, "ComputerPlayer"]] = kwargs.get("players", None)
        req_suit: tuple = kwargs.get("suit", None)
        req_value: tuple = kwargs.get("value", None)
        four_played: bool = kwargs.get("skip", None)
        king_played: bool = kwargs.get("king", None)
        penalty: int = kwargs.get("penalty", None)
        for card in self.hand:
            if center_card and center_card.can_play(card, **kwargs):
                if card.value in ("jack", "ace"):
                    return None
                return card
        return None
