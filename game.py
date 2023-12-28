from card import Card
from deck import Deck, DeckAlreadyEmptyError
from players import HumanPlayer, ComputerPlayer
import pygame as pg
from pygame.surfarray import array3d, make_surface
from pygame import Rect, Surface, image, font
from pygame.event import Event
import pygame_widgets as pgw  # type: ignore
from pygame_widgets.button import Button  # type: ignore
from pygame_widgets.mouse import Mouse, MouseState  # type: ignore
from typing import Callable, Optional, Union, Any
from functools import partial
from constants import SYMBOLS


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


class ImageButton(Button):
    def __init__(self, win: Surface, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(win, x, y, width, height, **kwargs)
        self.hover_image = self.darken_image(self.image)

    def darken_image(self, image: Surface) -> Surface:
        arr = array3d(image)
        arr = arr * 0.85
        return make_surface(arr)

    def draw(self):
        mouseState = Mouse.getMouseState()
        x, y = Mouse.getMousePos()
        if self.contains(x, y):
            if mouseState == MouseState.HOVER or mouseState == MouseState.DRAG:
                self.win.blit(self.hover_image, (self._x, self._y))
        else:
            self.win.blit(self.image, (self._x, self._y))


class SelectionMenu:
    def __init__(self, items: list[str]) -> None:
        self.items = items


class Game:
    # TODO:
    # - (Optional) Stop Macao button
    # - New window for value / color selection window after function cards are played
    # - next_turn and macao methods
    def __init__(self, player_number: int) -> None:
        """
        Represents game

        :param player_number: Number of players, must be at least 2 and not greater than 4
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
        self._current_card: Card = self._deck.deal()
        self._game_over: bool = False
        self._penalty_draw: int = 0
        self._current_player_index: int = 0
        self._current_player_move_status: bool = False

        self._game_rects: dict[str, list] = {"human_cards": [], "buttons": []}
        pg.init()
        self._min_width: int = 1050
        self._min_height: int = 800
        self._window_width: int = 1050
        self._window_height: int = 800
        self._background_color: tuple[int, int, int] = (34, 139, 34)
        self._rect_bg_color: tuple[int, int, int] = (255, 255, 255)
        self._text_color: tuple[int, int, int] = (0, 0, 0)
        self._font_size: int = 30
        self._font: font.Font = font.Font(None, self._font_size)
        self._card_width, self._card_height = image.load("images/hidden.png").get_size()
        self._window: Surface = pg.display.set_mode(
            (self._window_width, self._window_height)
        )

        self.render_buttons()

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
    def current_player_index(self) -> int:
        return self._current_player_index

    @property
    def current_player_move_status(self) -> bool:
        return self._current_player_move_status

    @property
    def penalty_draw(self) -> int:
        return self._penalty_draw

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
    def rect_bg_color(self) -> tuple[int, int, int]:
        return self._rect_bg_color

    @property
    def text_color(self) -> tuple[int, int, int]:
        return self._text_color

    @property
    def font(self) -> font.Font:
        return self._font

    @property
    def font_size(self) -> int:
        return self._font_size

    def increase_penalty(self, to_add: int) -> None:
        self._penalty_draw += to_add

    def draw_penalty(self, player: Union[HumanPlayer, ComputerPlayer]):
        self._penalty_draw = (
            len(self.deck) if len(self.deck) < self.penalty_draw else self.penalty_draw
        )
        self.take_cards(player, self.penalty_draw)
        self._penalty_draw = 0

    @staticmethod
    def select_symbol() -> int:
        selected_index: Optional[int] = None
        return selected_index

    def take_cards(
        self, player: Union[HumanPlayer, ComputerPlayer], number: int = 1
    ) -> None:
        """
        Takes a specified number of cards from the deck and gives them to the player.

        :param player: The player who will receive the cards.
        :param number: The number of cards to be taken, defaults to 1.
        """
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
        if self.current_player_move_status:
            self._current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
            self._current_player_move_status = False

    def play_card(
        self, played_card: Card, player: Union[HumanPlayer, ComputerPlayer]
    ) -> None:
        if self._current_card.can_play(played_card):
            played_card.play_effect(self)
            self.discarded_deck.add_card(self._current_card)
            self._current_card = played_card
            player.remove_card(played_card)
            self._current_player_move_status = True

    def check_card_click(self, mouse_pos: tuple[int, int]) -> Optional[Card]:
        """
        Check if a card has been clicked based on the mouse position.

        :param mouse_pos: The position of the mouse click.
        :return: The card that has been clicked, or None if no card was clicked.
        """
        rect_cards = list(zip(self.human_card_rects, self.players[0].hand))
        for rect, card in reversed(rect_cards):
            if rect.collidepoint(mouse_pos):
                return card
        return None

    def handle_quit_event(self) -> None:
        self._game_over = True

    def handle_mouse_button_down_event(self) -> None:
        """
        Handles the mouse button down event.

        This method checks if the right mouse button is pressed. If not, it gets the current mouse position.
        It then checks if a button or a card is clicked and performs the corresponding action.

        :return: None
        """
        if pg.mouse.get_pressed()[2]:
            return
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        if played_card := self.check_card_click(mouse_pos):
            print(f"Current card: {self._current_card}      Played card: {played_card}")
            self.play_card(played_card, self.players[0])

    def handle_video_resize_event(self, event: Event) -> None:
        """
        Handles the video resize event.

        :param event: The resize event.
        :return: None
        """
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
        self.render_buttons()

    def render_game(self, events: list[Event]) -> None:
        """
        Renders the game on the screen.

        This method fills the window with the background color, renders the center card,
        renders the buttons, and renders the cards for each player. Finally, it updates
        the display to show the changes.

        :return: None
        """
        self.window.fill(self.background_color)
        self.render_center_card()
        self.render_game_info()
        for player in self.players:
            self.render_cards(player)
        for button in self._game_rects["buttons"]:
            button.draw()
        pgw.update(events)
        pg.display.flip()

    def start(self) -> None:
        """
        Starts the game loop and handles various events such as quitting, mouse button down, and video resize.
        """
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
        card_image: Optional[Surface]
        button_width: int
        button_height: int
        padding: int = 5
        deck_len: int = len(self.discarded_deck) if not self.deck else len(self.deck)
        texts: list[str] = [str(deck_len), "NEXT", "PENALTY", "MAKAO!"]
        player: HumanPlayer = self.players[0]
        effects: list[Callable] = [
            partial(self.take_cards, player=player, number=1),
            self.next_turn,
            partial(self.draw_penalty, player=player),
            partial(self.macao, player=player),
        ]
        inactiveColour: tuple[int, int, int]
        hoverColour: tuple[float, ...]
        pressedColour: tuple[float, ...]
        for i, (message, effect) in enumerate(zip(texts, effects)):
            try:
                int(message)
                button_width = self.card_width
                button_height = self.card_height
                x = (self.window_width - button_width) // 2 + button_width + 5
                y = (self.window_height - button_height) // 2
                card_image = image.load("images/hidden.png")
                button = ImageButton(
                    self.window,
                    x,
                    y,
                    button_width,
                    button_height,
                    text=message,
                    image=card_image,
                    onClick=effect,
                )
            except ValueError:
                button_width = 90
                button_height = 50
                y = self.window_height - padding - button_height
                x = self.window_width - padding - i * button_width - (i - 1) * padding
                inactiveColour = self.rect_bg_color
                hoverColour = tuple(x*0.85 for x in self.rect_bg_color)
                pressedColour = tuple(x*0.9 for x in self.rect_bg_color)
                button = Button(
                    self.window,
                    x,
                    y,
                    button_width,
                    button_height,
                    text=message,
                    onClick=effect,
                    inactiveColour=inactiveColour,
                    hoverColour=hoverColour,
                    pressedColour=pressedColour,
                )
            self._game_rects["buttons"].append(button)

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

        position_dict: dict[int, dict[str, Any]] = self._get_position_dict(
            padding, card_height
        )
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
        """
        Calculates the total width required to display the cards in the hand.

        :param card_width: The width of a single card.
        :param num_rows: The number of rows in the card display.
        :param hand_len: The number of cards in the hand.
        :return: The total width required to display the cards.
        """
        return hand_len * (card_width // 2) + num_rows * card_width // 2

    def _calculate_start_coord(self, coord: str, total_width: int) -> int:
        """
        Calculate the starting coordinate based on the given coordinate and total width.

        :param coord: The coordinate to calculate the starting coordinate for. Must be either "x" or "y".
        :param total_width: The total width of the window.
        :return: The calculated starting coordinate.
        :raises WrongCoord: If the given coordinate is neither "x" nor "y".
        """
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

    def _get_position_dict(
        self, padding: int, card_height: int
    ) -> dict[int, dict[str, Any]]:
        """
        Returns a dictionary containing the position information for each player.

        :param padding: The padding value.
        :param card_height: The height of the card.
        :return: A dictionary where the keys represent the player index
            and the values represent the position information, including the start coordinate,
            fixed coordinate, and rotation flag.
        """
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
        """
        Scales the card dimensions based on the number of rows and allowed width.

        :param cards_per_row: Number of cards per row.
        :param max_total_width: Maximum total width allowed.
        :param allowed_width: Allowed width for scaling.
        :param num_rows: Number of rows.
        :param player: Player object.
        :return: Tuple containing the scaled card width, height, cards per row,
                 maximum total width, and number of rows.
        """
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
    ) -> Surface:
        """
        Load and scale an image based on the given card height, card width, and path.

        :param card_height: The desired height of the card image.
        :param card_width: The desired width of the card image.
        :param path: The path to the image file. Defaults to "images/hidden.png".
        :return: The loaded and scaled card image.
        """
        card_image: Surface = image.load(path)
        if card_height != self.card_height or card_width != self.card_width:
            card_image = pg.transform.scale(card_image, (card_width, card_height))
        return card_image


if __name__ == "__main__":
    game = Game(2)
    game.start()
