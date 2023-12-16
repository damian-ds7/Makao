from deck import Deck
from players import HumanPlayer, ComputerPlayer
import pygame as pg
from pygame import Rect, Surface, image
from typing import Union


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
        try:
            converted_player_number = int(player_number)
            if not 2 <= converted_player_number <= 4:
                raise WrongPlayerNumber(player_number)
            player_number = converted_player_number
        except ValueError:
            raise WrongPlayerNumber(player_number)

        self._players: list[Union[HumanPlayer, ComputerPlayer]] = [HumanPlayer()] + [
            ComputerPlayer() for _ in range(player_number - 1)
        ]
        self._deck: Deck = Deck()
        self.deal()
        self._game_over = False
        self.current_card = self.deck.deal()
        self._human_card_rects: list[Rect] = []

        pg.init()
        self.window_width = 900
        self.window_height = 700
        self.background_color = (34, 139, 34)
        self._card_width, self._card_height = image.load("images/hidden.png").get_size()
        self.window = pg.display.set_mode((self.window_width, self.window_height))

    @property
    def players(self) -> list[Union[HumanPlayer, ComputerPlayer]]:
        return self._players

    @property
    def deck(self) -> Deck:
        return self._deck

    @property
    def game_over(self) -> bool:
        return self._game_over

    @property
    def human_card_rects(self) -> list[Rect]:
        return self._human_card_rects

    @property
    def card_width(self) -> int:
        return self._card_width

    @property
    def card_height(self) -> int:
        return self._card_height

    def deal(self) -> None:
        for _ in range(5):
            for player in self.players:
                player.draw_card(self.deck)

    def start(self) -> None:
        while not self.game_over:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._game_over = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if pg.mouse.get_pressed()[2]:
                        continue
                    x, y = pg.mouse.get_pos()
                    self.check_card_click(x, y)

            self.window.fill(self.background_color)
            self.render_human_player_cards()
            for computer in self.players[1:]:
                if isinstance(computer, ComputerPlayer):
                    self.render_computer_players(computer)
            pg.display.flip()

        pg.quit()

    def render_center_card(self) -> None:
        card_image: pg.Surface = image.load(self.current_card.get_image_name())
        x: int = (self.window_width - self.card_width) // 2
        y: int = (self.window_height - self.card_height) // 2
        self.window.blit(card_image, (x, y))

    def render_computer_players(self, player: ComputerPlayer) -> None:
        hidden_card_image: Surface = image.load("images/hidden.png")
        padding: int = 10
        position: int = self.players.index(player)
        total_width: int = (
            len(self.players[0].hand) * (self.card_width // 2) + self.card_width // 2
        )
        if position == 1:
            y = padding
            start_x = (
                self.window_height - len(player.hand) * (self.card_width // 2)
            ) // 2
        elif position == 2:
            x = padding
            start_y = (
                self.window_height - len(player.hand) * (self.card_height // 2)
            ) // 2
            hidden_card_image = pg.transform.rotate(hidden_card_image, 90)
        elif position == 3:
            x = self.window_width - self.card_width - padding
            start_y = (
                self.window_height - len(player.hand) * (self.card_height // 2)
            ) // 2
            hidden_card_image = pg.transform.rotate(hidden_card_image, 90)

        for i, card in enumerate(player.hand):
            if position == 1:
                x = start_x + i * (self.card_width // 2)
            else:
                y = start_y + i * (self.card_height // 2)
            self.window.blit(hidden_card_image, (x, y))

    def render_human_player_cards(self) -> None:
        self._human_card_rects = []
        padding = 10
        total_width: int = (
            len(self.players[0].hand) * (self.card_width // 2) + self.card_width // 2
        )
        start_x = (self.window_width - total_width) // 2
        y: int = self.window_height - self.card_height - padding
        for i, card in enumerate(self.players[0].hand):
            x = start_x + i * (self.card_width // 2)
            card_image = image.load(card.get_image_name())
            self.window.blit(card_image, (x, y))
            card_rect = Rect(x, y, self.card_width, self.card_height)
            self._human_card_rects.append(card_rect)

    def check_card_click(self, x: int, y: int) -> None:
        for i in reversed(range(len(self.human_card_rects))):
            if self.human_card_rects[i].collidepoint(x, y):
                # A card was clicked! Do something with the card.
                clicked_card = self.players[0].hand[i]
                print(f"You clicked on {clicked_card}")
                break


game = Game(4)
game.start()
