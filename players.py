from card import Card
from typing import Optional


class HumanPlayer:
    def __init__(self) -> None:
        """
        Class representing human player with a deck of cards rank and makao status
        """
        self._cards: list[Card] = []
        self._rank: Optional[int] = None
        self._makao_status = False

    @property
    def makao_status(self) -> bool:
        return self._makao_status

    def add_card_to_deck(self, card: Card) -> None:
        self._cards.append(card)

    def player_info(self, human_computer: str = "Human player") -> str:
        cards: str = " ".join([str(card) for card in self._cards])
        return (
            f"{human_computer}\n"
            f"  Deck: {cards}\n"
            f"  Makao: {self._makao_status}\n"
            f"  Rank: {self._rank}"
        )


class ComputerPlayer(HumanPlayer):
    def __init__(self) -> None:
        """
        Class representing computer player with a deck of cards rank and makao status
        """
        super().__init__()

    def player_info(self, human_computer: str = "Computer player") -> str:
        return super().player_info(human_computer)
