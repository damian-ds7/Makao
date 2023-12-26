from card import Card
from deck import Deck, DeckAlreadyEmptyError
from players import HumanPlayer, ComputerPlayer
import pygame as pg
from pygame import Rect, Surface, image, font
from pygame.event import Event
from typing import Callable, Optional, Union, Any
from functools import partial


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


class Button:
    def __init__(
        self, x: int, y: int, effect: Callable, width: int = 75, height: int = 75
    ) -> None:
        self.rect: Rect = Rect(x, y, width, height)
        self._effect: Callable = effect

    @property
    def effect(self) -> Callable:
        return self._effect

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        if self.rect.collidepoint(mouse_pos):
            return True
        return False


class Game:
    # TODO:
    # - (Optional) Stop Macao button
    # - New window for value / color selection window after function cards are played
    # - next_turn and macao methods
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
        self._discarded_deck: Deck = Deck(empty=True)
        for _ in range(5):
            for player in self._players:
                self.take_cards(player)
        self._current_card = self._deck.deal()
        self._game_over = False

        self._game_rects: dict[str, list] = {"human_cards": [], "buttons": []}
        pg.init()
        self._min_width: int = 1050
        self._min_height: int = 800
        self._window_width: int = 1050
        self._window_height: int = 800
        self._background_color: tuple[int, int, int] = (34, 139, 34)
        self._text_color: tuple[int, int, int] = (0, 0, 0)
        self._font: font.Font = font.Font(None, 30)
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
    def discarded_deck(self) -> Deck:
        return self._discarded_deck

    @property
    def game_over(self) -> bool:
        return self._game_over

    @property
    def human_card_rects(self) -> list[Rect]:
        return self._game_rects["human_cards"]

    @property
    def card_width(self) -> int:
        return self._card_width

    @property
    def card_height(self) -> int:
        return self._card_height

    @property
    def window(self) -> Surface:
        return self._window

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
    def background_color(self) -> tuple[int, int, int]:
        return self._background_color

    @property
    def text_color(self) -> tuple[int, int, int]:
        return self._text_color

    @property
    def font(self) -> font.Font:
        return self._font

    def take_cards(
        self, player: Union[HumanPlayer, ComputerPlayer], number: int = 1
    ) -> None:
        try:
            player.draw_card(self.deck, number)
        except DeckAlreadyEmptyError:
            if not self.discarded_deck:
                return
            self.discarded_deck.shuffle()
            self._deck = self.discarded_deck
            self._discarded_deck = Deck(empty=True)
            player.draw_card(self.deck, number)

    def macao(self, player: Union[HumanPlayer, ComputerPlayer]) -> None:
        print("clicked macao")

    def next_turn(self) -> None:
        print("clicked next")

    def play_card(
        self, played_card: Card, player: Union[HumanPlayer, ComputerPlayer]
    ) -> None:
        if self._current_card.can_play(played_card):
            # played_card.play_effect(self)
            self.discarded_deck.add_card(self._current_card)
            self._current_card = played_card
            player.remove_card(played_card)

    def check_card_click(self, mouse_pos: tuple[int, int]) -> Optional[Card]:
        rect_cards = list(zip(self.human_card_rects, self.players[0].hand))
        for rect, card in reversed(rect_cards):
            if rect.collidepoint(mouse_pos):
                return card
        return None

    def check_button_click(self, mouse_pos: tuple[int, int]) -> Optional[Button]:
        for button in self._game_rects["buttons"]:
            if button.check_click(mouse_pos):
                return button
        return None

    def handle_quit_event(self) -> None:
        self._game_over = True

    def handle_mouse_button_down_event(self) -> None:
        if pg.mouse.get_pressed()[2]:
            return
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        if clicked_button := self.check_button_click(mouse_pos):
            clicked_button.effect()
        elif played_card := self.check_card_click(mouse_pos):
            print(f"Current card: {self._current_card}      Played card: {played_card}")
            self.play_card(played_card, self.players[0])

    def handle_video_resize_event(self, event) -> None:
        width, height = event.size
        if width < self.min_height or height < self.min_height:
            self._window_width, self._window_height = (
                self.min_width,
                self.min_height,
            )
        else:
            self._window_width, self._window_height = width, height
        self._window = pg.display.set_mode(
            (self.window_width, self.window_height), pg.RESIZABLE
        )

    def render_game(self) -> None:
        self.window.fill(self.background_color)
        self.render_center_card()
        self.render_buttons()
        for player in self.players:
            self.render_cards(player)
        pg.display.flip()

    def start(self) -> None:
        while not self.game_over:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.handle_quit_event()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.handle_mouse_button_down_event()
                elif event.type == pg.VIDEORESIZE:
                    self.handle_video_resize_event(event)
            self.render_game()
        pg.quit()

    def render_buttons(self) -> None:
        """
        Renders clickable buttons: Deck to draw cards, Macao! and Next Buttons
        """
        self._game_rects["buttons"] = []
        x: int
        y: int
        button: Button
        text: Surface
        card_image: Surface
        text_width: int
        text_height: int
        text_x: int
        text_y: int
        button_color: tuple[int, int, int] = (255, 255, 255)
        button_width: int
        button_height: int
        padding: int = 5
        deck_len: int = len(self.discarded_deck) if not self.deck else len(self.deck)
        texts: list[str] = [str(deck_len), "NEXT", "MAKAO!"]
        player: HumanPlayer = self.players[0]
        effects: list[Callable] = [
            partial(self.take_cards, player=player, number=1),
            partial(self.next_turn),
            partial(self.macao, player=player),
        ]
        for i in range(3):
            text = text = self.font.render(texts[i], True, self.text_color)
            text_width, text_height = text.get_size()

            if not i:
                button_width = self.card_width
                button_height = self.card_height
                x = (self.window_width - button_width) // 2 + button_width + 5
                y = (self.window_height - button_height) // 2
                text_x = x + (button_width - text_width) // 2
                text_y = y + (button_height - text_height) // 2
                card_image = image.load("images/hidden.png")
                self._window.blit(card_image, (x, y))
            else:
                button_width = 90
                button_height = 50
                y = self.window_height - padding - button_height
                x = self.window_width - padding - i * button_width - (i - 1) * padding
                text_x = x + (button_width - text_width) // 2
                text_y = y + (button_height - text_height) // 2

            button = Button(
                x, y, effect=effects[i], width=button_width, height=button_height
            )
            self._game_rects["buttons"].append(button)
            if not i:
                self._window.blit(card_image, (x, y))
            else:
                pg.draw.rect(self.window, button_color, button.rect)
            self.window.blit(text, (text_x, text_y))

    def render_center_card(self) -> None:
        """
        Renders current center card and hidden deck of cards that player can draw from
        """
        card_image: Surface = image.load(self._current_card.get_image_name())
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
        padding: int = 5
        position: int = self.players.index(player)

        if not 0 <= position <= 3:
            raise WrongPosition(position)

        card_width: int
        card_height: int
        card_width, card_height = self.card_width, self.card_height
        cards_per_row: int = 10
        hand_len: int = len(player.hand)
        num_rows: int = self._calculate_num_rows(hand_len, cards_per_row)
        allowed_width: int = self._calculate_allowed_width(cards_per_row)
        max_total_width: int = self._calculate_total_width(
            card_width, num_rows, hand_len
        )
        (
            card_width,
            card_height,
            cards_per_row,
            max_total_width,
            num_rows,
        ) = self._scale_card(
            cards_per_row,
            max_total_width,
            allowed_width,
            num_rows,
            player,
        )

        position_dict: dict[int, dict[str, Any]] = self._get_position_dict(padding, card_height)
        if position != 0:
            card_image: Surface = self._load_scale_image(card_height, card_width)
        else:
            self._game_rects["human_cards"] = []

        total_width = min(max_total_width, allowed_width)
        max_total_width -= total_width

        start_coord: int = self._calculate_start_coord(
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
                start_coord = self._calculate_start_coord(
                    position_dict[position]["start_coord"], total_width
                )
                if position in [0, 1]:
                    start_x = start_coord
                    y = y - ((-1) ** position) * (card_height + padding)
                else:
                    start_y = start_coord
                    x = x + (-1) ** (position - 2) * (card_height + padding)

            if position == 0:
                x = self._shift_coord(start_x, i, cards_per_row, card_width)
                card_image = self._load_scale_image(
                    card_height, card_width, card.get_image_name()
                )
                card_rect: Rect = Rect(x, y, card_width, card_height)
                self._game_rects["human_cards"].append(card_rect)
            elif position == 1:
                x = self._shift_coord(start_x, i, cards_per_row, card_width)
            else:
                y = self._shift_coord(start_y, i, cards_per_row, card_width)

            self.window.blit(card_image, (x, y))

    def _calculate_num_rows(self, hand_len: int, cards_per_row: int) -> int:
        num_rows = hand_len // cards_per_row
        if hand_len % cards_per_row > 0:
            num_rows += 1
        return num_rows

    def _calculate_allowed_width(self, cards_per_row: int) -> int:
        return cards_per_row * (self.card_width // 2) + self.card_width // 2

    def _calculate_total_width(
        self, card_width: int, num_rows: int, hand_len: int
    ) -> int:
        return hand_len * (card_width // 2) + num_rows * card_width // 2

    def _calculate_start_coord(self, coord: str, total_width: int) -> int:
        coord = coord.lower()
        if not (coord == "x" or coord == "y"):
            raise WrongCoord(coord)

        if coord == "x":
            return (self.window_width - total_width) // 2
        else:
            return (self.window_height - total_width) // 2

    @staticmethod
    def _shift_coord(
        coord: int, index: int, cards_per_row: int, card_width: int
    ) -> int:
        """
        Adjusts shifting coordinate based on cards position in player's deck
        """
        index %= cards_per_row
        return coord + index * (card_width // 2)

    def _get_position_dict(self, padding, card_height: int) -> dict[int, dict[str, Any]]:
        return {
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

    def _scale_card(
        self,
        cards_per_row: int,
        max_total_width: int,
        allowed_width: int,
        num_rows: int,
        player,
    ) -> tuple[int, ...]:
        if num_rows <= 3:
            return (
                self.card_width,
                self.card_height,
                cards_per_row,
                max_total_width,
                num_rows,
            )

        num_rows = 3
        cards_per_row = len(player.hand) // num_rows
        if len(player.hand) % num_rows > 0:
            cards_per_row += 1
        scale_factor = allowed_width / (
            cards_per_row * (self.card_width // 2) + self.card_width // 2
        )
        card_width = int(self.card_width * scale_factor)
        card_height = int(self.card_height * scale_factor)
        max_total_width = self._calculate_total_width(
            card_width, num_rows, len(player.hand)
        )
        return card_width, card_height, cards_per_row, max_total_width, num_rows

    def _load_scale_image(
        self, card_height: int, card_width: int, path: str = "images/hidden.png"
    ):
        card_image: Surface = image.load(path)
        if card_height != self.card_height or card_width != self.card_width:
            card_image = pg.transform.scale(card_image, (card_width, card_height))
        return card_image


if __name__ == "__main__":
    game = Game(2)
    game.start()
