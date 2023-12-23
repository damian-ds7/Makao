from deck import Deck
from players import HumanPlayer, ComputerPlayer
import pygame as pg
from pygame import Rect, Surface, image
from typing import Union, Tuple


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
    # TODO:
    # - Macao button
    # - Next button
    # - (Optional) Stop Macao button
    # - Click handling
    # - New window for value / color selection window after function cards are played
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
        self._current_card = self._deck.deal()
        self.deal()
        self._game_over = False

        self._human_card_rects: list[Rect] = []

        pg.init()
        self._min_width: int = 1050
        self._min_height: int = 800
        self._window_width: int = 1050
        self._window_height: int = 800
        self._background_color: tuple = (34, 139, 34)
        self._card_width, self._card_height = image.load("images/hidden.png").get_size()
        self._window: Surface = pg.display.set_mode(
            (self._window_width, self._window_height)
        )

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

    @property
    def window_width(self) -> int:
        return self._window_width

    @property
    def window_height(self) -> int:
        return self._window_height

    @property
    def min_width(self) -> int:
        return self._min_width

    @property
    def min_height(self) -> int:
        return self._min_height

    @property
    def background_color(self) -> Tuple[int, int, int]:
        return self._background_color

    def deal(self, starting_cards: int = 5) -> None:
        # TODO: reshuffling the deck when it's empty
        for _ in range(starting_cards):
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
                        self._window_width, self._window_height = (
                            self.min_width,
                            self.min_height,
                        )
                    else:
                        self._window_width, self._window_height = width, height
                    self._window = pg.display.set_mode(
                        (self.window_width, self.window_height), pg.RESIZABLE
                    )

            self._window.fill(self.background_color)
            self.render_center_card()
            for player in self.players:
                self.render_cards(player)
            pg.display.flip()

        pg.quit()

    def render_center_card(self) -> None:
        card_image: Surface = image.load(self._current_card.get_image_name())
        x: int = (self.window_width - self.card_width) // 2
        y: int = (self.window_height - self.card_height) // 2
        self._window.blit(card_image, (x, y))

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
            return coord + index * (card_width // 2)

        def calculate_total_width(card_width: int, num_rows: int) -> int:
            return len(player.hand) * (card_width // 2) + num_rows * card_width // 2

        def scale_card(
            card_width: int,
            card_height: int,
            cards_per_row: int,
            max_total_width: int,
            allowed_width: int,
            num_rows: int,
        ) -> Tuple[int, int, int, int, int]:
            """
            Based on total width modifies number of cards in row, card width and height
            """
            if not num_rows > 3:
                return card_width, card_height, cards_per_row, max_total_width, num_rows

            num_rows = 3
            cards_per_row = len(player.hand) // num_rows
            if len(player.hand) % num_rows > 0:
                cards_per_row += 1
            scale_factor = allowed_width / (
                cards_per_row * (card_width // 2) + card_width // 2
            )
            card_width = int(card_width * scale_factor)
            card_height = int(card_height * scale_factor)
            max_total_width = calculate_total_width(card_width, num_rows)
            return card_width, card_height, cards_per_row, max_total_width, num_rows

        def load_scale_image(
            card_height: int, card_width: int, path: str = "images/hidden.png"
        ):
            card_image: Surface = image.load(path)
            if card_height != self.card_height or card_width != self.card_width:
                card_image = pg.transform.scale(card_image, (card_width, card_height))
            return card_image

        padding: int = 5
        position: int = self.players.index(player)

        if not 0 <= position <= 3:
            raise WrongPosition(position)

        card_width, card_height = self.card_width, self.card_height
        cards_per_row: int = 10
        num_rows = len(player.hand) // cards_per_row
        if len(player.hand) % cards_per_row > 0:
            num_rows += 1

        allowed_width: int = cards_per_row * (card_width // 2) + card_width // 2
        max_total_width: int = calculate_total_width(card_width, num_rows)

        card_width, card_height, cards_per_row, max_total_width, num_rows = scale_card(
            card_width,
            card_height,
            cards_per_row,
            max_total_width,
            allowed_width,
            num_rows,
        )
        position_dict: dict[int, dict] = {
            0: {
                "start_coord": "x",
                "fixed_coord": self.window_height - card_height - padding,
                "rotate": False,
            },
            1: {"start_coord": "x", "fixed_coord": padding, "rotate": False},
            2: {"start_coord": "y", "fixed_coord": padding, "rotate": True},
            3: {
                "start_coord": "y",
                "fixed_coord": self.window_width - card_height - padding,
                "rotate": True,
            },
        }

        if position != 0:
            card_image: Surface = load_scale_image(card_height, card_width)

        total_width = min(max_total_width, allowed_width)
        max_total_width -= total_width

        start_coord: int = calculate_start_coord(
            position_dict[position]["start_coord"], total_width
        )
        fixed_coord: int = position_dict[position]["fixed_coord"]
        if position_dict[position]["rotate"]:
            card_image = pg.transform.rotate(card_image, 90)

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
                    y = y + -((-1) ** position) * (card_height + padding)
                else:
                    start_y = start_coord
                    x = x + (-1) ** (position - 2) * (card_height + padding)

            if position == 0:
                x = shift_coord(start_x, i)
                card_image = load_scale_image(
                    card_height, card_width, card.get_image_name()
                )
                card_rect = Rect(x, y, card_width, card_height)
                self._human_card_rects.append(card_rect)
            else:
                if position == 1:
                    x = shift_coord(start_x, i)
                else:
                    y = shift_coord(start_y, i)

            self._window.blit(card_image, (x, y))

    def check_card_click(self, x: int, y: int) -> None:
        rect_cards = list(zip(self.human_card_rects, self.players[0].hand))
        for rect, card in reversed(rect_cards):
            if rect.collidepoint(x, y):
                clicked_card = card
                print(f"You clicked on {clicked_card}")
                break


if __name__ == "__main__":
    game = Game(2)
    game.start()
