from deck import Deck
from players import HumanPlayer, ComputerPlayer
import pygame as pg
from pygame import Rect, Surface, image
from typing import Union


class WrongCoord(ValueError):
    def __init__(
        self, coord: str, message: str = "Coord must be either x or y"
    ) -> None:
        super().__init__(message, coord)


class WrongPosition(ValueError):
    def __init__(
        self, position: int, message: str = "Position must be a number between 0 and 3"
    ) -> None:
        super().__init__(message, position)


class WrongPlayerNumber(ValueError):
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
        # try:
        #     converted_player_number = int(player_number)
        #     if not 2 <= converted_player_number <= 4:
        #         raise WrongPlayerNumber(player_number)
        #     player_number = converted_player_number
        # except ValueError:
        #     raise WrongPlayerNumber(player_number)

        self._players: list[Union[HumanPlayer, ComputerPlayer]] = [HumanPlayer()] + [
            ComputerPlayer() for _ in range(player_number - 1)
        ]
        self._deck: Deck = Deck()
        self.deal()
        self._game_over = False
        self.current_card = self.deck.deal()
        self._human_card_rects: list[Rect] = []

        pg.init()
        self.min_width = 900
        self.min_height = 760
        self.window_width = 900
        self.window_height = 760
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
        for _ in range(30):
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
                elif event.type == pg.VIDEORESIZE:
                    width, height = event.size
                    if width < 900 or height < self.min_height:
                        self.window_width, self.window_height = 900, 700
                    else:
                        self.window_width, self.window_height = width, height
                    self.window = pg.display.set_mode(
                        (self.window_width, self.window_height), pg.RESIZABLE
                    )

            self.window.fill(self.background_color)
            self.render_center_card()
            for player in self.players:
                self.render_cards(player)
            pg.display.flip()

        pg.quit()

    def render_center_card(self) -> None:
        card_image: pg.Surface = image.load(self.current_card.get_image_name())
        x: int = (self.window_width - self.card_width) // 2
        y: int = (self.window_height - self.card_height) // 2
        self.window.blit(card_image, (x, y))

    def render_cards(self, player: Union[ComputerPlayer, HumanPlayer]) -> None:
        """
        Renders players cards based on their number:
            0 - Human, bottom, visible cards
            1 - Computer, top
            2 - Computer, left
            3 - Computer, right
        All computers' cards are rendered upside down

        :param player: Player object from list of players
        :type player: Union[ComputerPlayer, HumanPlayer]
        :raises WrongPosition: When wrong index is given
        """
        hidden_card_image: Surface = image.load("images/hidden.png")
        padding: int = 5
        position: int = self.players.index(player)

        if not 0 <= position <= 3:
            raise WrongPosition(position)

        cards_per_row: int = 10
        num_rows = len(player.hand) // cards_per_row
        if len(player.hand) % cards_per_row > 0:
            num_rows += 1
        allowed_width: int = (
            cards_per_row * (self.card_width // 2) + self.card_width // 2
        )
        max_total_width: int = (
            len(player.hand) * (self.card_width // 2) + num_rows * self.card_width // 2
        )
        position_dict: dict[int, dict] = {
            0: {
                "start_coord": "x",
                "fixed_coord": self.window_height - self.card_height - padding,
                "rotate": False,
            },
            1: {"start_coord": "x", "fixed_coord": padding, "rotate": False},
            2: {"start_coord": "y", "fixed_coord": padding, "rotate": True},
            3: {
                "start_coord": "y",
                "fixed_coord": self.window_width - self.card_height - padding,
                "rotate": True,
            },
        }

        def calculate_start_coord(coord: str, total_width: int) -> int:
            coord = coord.lower()
            if not (coord == "x" or coord == "y"):
                raise WrongCoord(coord)

            if coord == "x":
                return (self.window_width - total_width) // 2
            else:
                return (self.window_height - total_width) // 2

        def shift_coord(coord: int, index: int) -> int:
            """
            Adjusts shifting coordinate based on cards position in player's deck
            """
            index %= cards_per_row
            return coord + index * (self.card_width // 2)

        total_width = min(max_total_width, allowed_width)
        max_total_width -= total_width

        start_coord: int = calculate_start_coord(
            position_dict[position]["start_coord"], total_width
        )
        fixed_coord: int = position_dict[position]["fixed_coord"]
        if position_dict[position]["rotate"]:
            hidden_card_image = pg.transform.rotate(hidden_card_image, 90)

        if position in [0, 1]:
            start_x = start_coord
            y = fixed_coord
        else:
            start_y = start_coord
            x = fixed_coord

        for i, card in enumerate(player.hand):
            if i != 0 and i % cards_per_row == 0:
                total_width = min(max_total_width, allowed_width)
                max_total_width -= total_width
                start_coord = calculate_start_coord(
                    position_dict[position]["start_coord"], total_width
                )
                if position in [0, 1]:
                    start_x = start_coord
                    y = y + -((-1) ** position) * (self.card_height + padding)
                else:
                    start_y = start_coord
                    y = y + (-1) ** (position - 2) * (self.card_height + padding)

            if position == 0:
                x = shift_coord(start_x, i)
                card_image = image.load(card.get_image_name())
                self.window.blit(card_image, (x, y))
                card_rect = Rect(x, y, self.card_width, self.card_height)
                self._human_card_rects.append(card_rect)
            else:
                if position == 1:
                    x = shift_coord(start_x, i)
                else:
                    y = shift_coord(start_y, i)
                self.window.blit(hidden_card_image, (x, y))

    def check_card_click(self, x: int, y: int) -> None:
        rect_cards = list(zip(self.human_card_rects, self.players[0].hand))
        for rect, card in reversed(rect_cards):
            if rect.collidepoint(x, y):
                clicked_card = card
                print(f"You clicked on {clicked_card}")
                break


game = Game(1)
game.start()
