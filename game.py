from typing import Union
from deck import Deck
from players import HumanPlayer, ComputerPlayer


class WrongPlayerNumber(Exception):
    def __init__(
        self,
        player_number,
        message="Number of players must be an int between 2 and 4",
    ) -> None:
        super().__init__(message, player_number)


class Game:
    def __init__(self, player_number: int) -> None:
        """
        Represents game

        :param player_number: Number of players, must be at least 2 and not greater than 4
        :type player_number: int
        :raises WrongPlayerNumber: If the number of players is not within the allowed range.
        """
        if type(player_number) is not int or not 2 <= player_number <= 4:
            raise WrongPlayerNumber(player_number)
        self._players = [HumanPlayer()] + [ComputerPlayer() for i in range(player_number - 1)]
        self._deck = Deck()
        self.deal()

    @property
    def players(self) -> list[Union[HumanPlayer, ComputerPlayer]]:
        return self._players

    def deal(self):
        for _ in range(5):
            for player in self.players:
                card = self._deck.deal()
                player.add_card_to_deck(card)
