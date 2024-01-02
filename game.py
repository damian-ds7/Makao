from card import Card
from constants import SUITS
from deck import Deck, DeckAlreadyEmptyError
from players import HumanPlayer, ComputerPlayer
from players import PlayNotAllowedError
import pygame as pg
from pygame.surfarray import array3d, make_surface
from pygame import Rect, Surface, image, font
from pygame.event import Event
import pygame_widgets as pgw  # type: ignore
from pygame_widgets.button import Button  # type: ignore
from pygame_widgets.mouse import Mouse, MouseState  # type: ignore
from typing import Callable, Optional, Union, Any
from functools import partial
from time import sleep


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
        self.hover_image: Surface = self.modify_brightness(self.image, 0.85)
        self.click_image: Surface = self.modify_brightness(self.image, 0.75)
        self.inactive_image: Surface = self.image

    def modify_brightness(self, image: Surface, multiplier: float) -> Surface:
        arr = array3d(image)
        arr = arr * multiplier
        return make_surface(arr)

    def draw(self, **kwargs) -> None:
        mouseState = Mouse.getMouseState()
        x, y = Mouse.getMousePos()

        if self.contains(x, y):
            if mouseState == MouseState.HOVER or mouseState == MouseState.DRAG:
                self.image = self.hover_image
            elif mouseState == MouseState.RELEASE and self.clicked:
                self.image = self.inactive_image
            elif mouseState == MouseState.CLICK:
                self.image = self.click_image
        else:
            self.image = self.inactive_image

        self.win.blit(self.image, (self._x, self._y))
        if kwargs:
            new_len: str = kwargs.get("new_len", None)
            self.setText(new_len)
        self.textRect: Rect = self.text.get_rect()
        self.alignTextRect()
        self.win.blit(self.text, self.textRect)


class SelectionMenu:
    def __init__(
        self,
        items: list[str],
        screen: Surface,
        button_height: int = 30,
        button_width: int = 90,
    ) -> None:
        self.screen: Surface = screen
        padding: int = 5
        font_size: int = 20
        window_height: int = len(items) * (button_height + padding) + padding
        window_width: int = button_width + 2 * padding
        x: int = self.screen.get_width() // 2 - window_width // 2
        y: int = self.screen.get_height() // 2 - window_height // 2
        inactive_color: tuple[int, int, int] = (255, 255, 255)
        hover_color: tuple[float, ...] = tuple(x * 0.85 for x in inactive_color)

        self.rect: Rect = Rect(x, y, window_width, window_height)
        self.background_color: tuple[int, int, int] = (34, 139, 34)
        self.buttons: list[Button] = []

        for i, text in enumerate(items):
            button = Button(
                self.screen,
                self.rect.x + padding,
                self.rect.y + i * (button_height + padding) + padding,
                button_width,
                button_height,
                text=text,
                fontSize=font_size,
                inactiveColour=inactive_color,
                hoverColour=hover_color,
            )
            self.buttons.append(button)

    def run(self) -> int:
        running: bool = True
        selected: int
        while running:
            events: list[Event] = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    continue
            # pg.draw.rect(self.screen, self.background_color, self.rect)
            for i, button in enumerate(self.buttons):
                if button.clicked:
                    selected = i
                    running = False
            pgw.update(events)
            pg.display.update(self.rect)
        return selected


class Game:
    # TODO:
    # - (Optional) Stop Macao button
    def __init__(self, player_number: int) -> None:
        """
        Represents a game of Makao.

        :param player_number: The number of players in the game. Must be at least 2 and not greater than 4.
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
                player.draw_card(self.deck)
                player.reset_turn_status()
        self._center_card: Card = self._deck.deal()
        self._game_over: bool = False
        self._current_player_index: int = 0
        self._game_params: dict[str, Any] = {}
        # self._finished_move: bool = False
        self.played_card: Optional[Card] = None
        self._finished_players: list[Union[HumanPlayer, ComputerPlayer]] = []

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
    def finished_players(self) -> list[Union[HumanPlayer, ComputerPlayer]]:
        return self._finished_players

    def player_finish(self, player: Union[HumanPlayer, ComputerPlayer]) -> None:
        self.finished_players.append(player)

    def check_if_finished(self, player: Union[HumanPlayer, ComputerPlayer]) -> None:
        if len(player.hand) == 0:
            self.player_finish(player)

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

    def change_current_player(self, decrement: bool = False) -> None:
        if not decrement:
            self._current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
        else:
            self._current_player_index = (self.current_player_index - 1) % len(
                self.players
            )

    @property
    def center_card(self) -> Card:
        return self._center_card

    @property
    def game_params(self) -> dict[str, Any]:
        return self._game_params

    # @property
    # def finished_move(self) -> bool:
    #     return self._finished_move

    @property
    def get_skip(self) -> int:
        return self.game_params.get("skip", None) or 0

    def increment_skip(self) -> None:
        val = self.game_params.get("skip", None) or 0
        self.game_params.update({"skip": val + 1})

    def reset_skip(self) -> None:
        if self.game_params.get("skip", None):
            self.game_params.pop("skip")

    @property
    def get_penalty(self) -> int:
        return self.game_params.get("penalty", None) or 0

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

    def get_previous_player(self) -> Union[HumanPlayer, ComputerPlayer]:
        return self.players[self.current_player_index - 1]

    def get_current_player(self) -> Union[HumanPlayer, ComputerPlayer]:
        return self.players[self.current_player_index]

    def increase_penalty(self, to_add: int) -> None:
        key, val = "penalty", self.game_params.get("penalty", None) or 0
        self.game_params.update({key: val + to_add})

    def reset_penalty(self):
        self.game_params.pop("penalty")

    def draw_penalty(self, player: Union[HumanPlayer, ComputerPlayer], number: int = 0):
        player.penalty = True
        draw: int = self.get_penalty if not number else number
        if not draw:
            return
        self.reset_penalty()
        self.reset_king()
        self.take_cards(player, draw)
        player.penalty = False

    def king_played(self, **kwargs) -> None:
        """
        Updates the game state when a king card is played.

        :param previous: Indicates which player will have to draw penalty
        :return: None
        """
        previous: bool = kwargs.get("previous", None)
        player = self.get_current_player()
        self.game_params.update({"king": True})
        self.increase_penalty(5)
        if previous:
            player.skip_turns += 2  # Additional turn added to compensate for next_turn
            player.played_king = True
        self.next_turn(backwards=previous)

    def reset_king(self) -> None:
        if self.game_params.get("king", None):
            self.game_params.pop("king")
            self.reset_penalty()

    def selection(self, items: list[str]) -> None:
        """
        Allows the player to make a selection from a list of items.

        :param items: The list of items to choose from.
        :return: None
        """
        if not self.current_player_index:
            menu: SelectionMenu = SelectionMenu(items, self.window)
            selected_index: int = menu.run()
        else:
            # TODO: algorithm for player to adapt to required cards
            pass

        #  number of turns in tuples in one more than in the rules to account for casting player's next_turn()
        if self.center_card.value == "jack":
            self.game_params.update({"value": (items[selected_index], 5)})
        else:
            self.game_params.update({"suit": (items[selected_index], 2)})
        self.next_turn()

    def take_cards(
        self, player: Union[HumanPlayer, ComputerPlayer], number: int = 1
    ) -> None:
        """
        Take a specified number of cards from the deck and give them to a player.

        :param player: The player who will receive the cards.
        :param number: The number of cards to be taken, defaults to 1.
        """
        if self.players.index(player) != self.current_player_index or self.game_params.get("skip", None):
            return

        if self.get_penalty:
            self.draw_penalty(player)
            return

        try:
            while number != 0:
                player.draw_card(self.deck)
                number -= 1
        except DeckAlreadyEmptyError:
            if not self.discarded_deck:
                return
            self.discarded_deck.shuffle()
            self._deck = self.discarded_deck
            self._discarded_deck = Deck(empty=True)
            while number != 0:
                player.draw_card(self.deck)
                number -= 1

        player.makao_set_reset(False)

    def makao(self, player: Union[HumanPlayer, ComputerPlayer]) -> None:
        if (
            len(player.hand) > 1
            or self.players.index(player) != self.current_player_index
        ):
            return
        else:
            player.makao_set_reset(True)
            print("clicked macao")

    def makao_out(self, player: Union[HumanPlayer, ComputerPlayer]):
        if len(player.hand) != 0:
            return
        self.makao(player)
        self.next_turn()

    def stop_makao(self, player: Union[HumanPlayer, ComputerPlayer]) -> None:
        if self.players.index(player) != self.current_player_index:
            return
        previous_player: Union[HumanPlayer, ComputerPlayer] = self.get_previous_player()
        if len(previous_player.hand) in [0, 1] and not player.makao_status:
            self.change_current_player(decrement=True)
            self.draw_penalty(previous_player, number=5)
            self.change_current_player()

    def update_req_params(self) -> None:
        """
        Update the required parameters for the game.

        This method updates the required parameters for the game based on the current game parameters.
        It decreases the number of turns left for each required parameter by 1, and removes the parameter
        if the number of turns left becomes 0.

        :return: None
        """
        reqs: list[Optional[tuple[str, int]]] = [
            self.game_params.get("suit", None),
            self.game_params.get("value", None),
        ]
        for req in reqs:
            if req:
                turns_left: int = req[1]
                turns_left -= 1
                req = (req[0], turns_left)
                key = "suit" if req[0] in SUITS else "value"
                if not turns_left:
                    self.game_params.pop(key)
                else:
                    self.game_params.update({key: req})

    def next_turn(self, backwards: bool = False) -> None:
        player: Union[HumanPlayer, ComputerPlayer] = self.get_current_player()
        # if self.penalty_draw:
        #     self.draw_penalty(player)
        self.check_if_finished(player)
        if self.get_penalty and not player.cards_played:
            self.draw_penalty(player)
        if self.get_skip and not self.played_card:
            player.skip_turns = self.get_skip
            self.reset_skip()
        if player.check_moved() or player.skip_turns:
            player.skip_turns -= 1 if player.skip_turns else 0
            player.reset_turn_status()
            self.played_card = None
            self.change_current_player(decrement=backwards)

    def play_card(
        self, played_card: Card, player: Union[HumanPlayer, ComputerPlayer]
    ) -> None:
        """
        Play a card and update the game state.

        :param played_card: The card to be played.
        :param player: The player who played the card.
        :return: None
        """
        try:
            if self.center_card.can_play(played_card, **self.game_params):
                if player.cards_played == 4 and len(player.hand) == 1:
                    raise PlayNotAllowedError(
                        "If played card is the last card in deck only up to 3 cards can"
                        " be played before"
                    )
                player.play_card(played_card)
                if player.cards_played == 1:
                    self.update_req_params()
                self.discarded_deck.add_card(self.center_card)
                self._center_card = played_card
                played_card.play_effect(self)
        except PlayNotAllowedError:
            return

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

    def play_turn(self) -> None:
        """
        Plays a turn in the game.

        This method determines the actions to be taken by the current player during their turn.
        It checks if the player needs to skip turns, draw penalty cards, play a card, or take cards from the center.
        The method also updates the game state and moves to the next turn.

        :return: None
        """
        player: Union[HumanPlayer, ComputerPlayer] = self.get_current_player()
        if player in self.finished_players:
            self.next_turn()
            return
        if player.skip_turns:
            if player.played_king:
                self.draw_penalty(player)
                player.played_king = False
            self.next_turn()
            player.skip_turns -= 1
            return
        if self.current_player_index:
            self.stop_makao(player)
            players = self.players.copy()
            game_state: dict[str, Union[list, Card]] = {
                "players": players,
                "center": self.center_card,
            }
            game_state.update(self.game_params)
            self.played_card: Optional[Card] = player.find_best_play(**game_state)  # type: ignore
            if not self.played_card:
                if self.get_penalty:
                    self.draw_penalty(player)
                else:
                    self.take_cards(player)
                self.next_turn()
                sleep(1)
                return
            print(
                f"Current card: {self.center_card}      Played card: {self.played_card}"
            )
            self.play_card(self.played_card, player)
            if len(player.hand) == 1:
                self.makao(player)
            self.next_turn()
            sleep(1)
        else:
            print(
                f"Current card: {self.center_card}      Played card:"
                f" {self.played_card}"
            )
            self.play_card(self.played_card, player)

    def handle_quit_event(self) -> None:
        self._game_over = True

    def handle_mouse_button_down_event(self) -> Optional[Card]:
        """
        Handles the mouse button down event.

        This method checks if the right mouse button is pressed. If not, it gets the current mouse position.
        It then checks if a button or a card is clicked and assigns clicked card to played_card attribute

        :return: None
        """
        if pg.mouse.get_pressed()[2]:
            return None
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        if card := self.check_card_click(mouse_pos):
            return card
        return None

    def handle_video_resize_event(self, event: Event) -> None:
        """
        Handle the video resize event.

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
        Render the game on the screen.

        This method fills the window with the background color, renders the center card,
        renders the buttons, and renders the cards for each player. Finally, it updates
        the display to show the changes.

        :return: None
        """
        self.window.fill(self.background_color)
        self.render_center_card()
        self.render_game_info()
        for player in self.players:
            self.render_cards(player, all_visible=True)
        for button in self._game_rects["buttons"]:
            try:
                new_len = str(
                    len(self.discarded_deck) if not self.deck else len(self.deck)
                )
                button.draw(new_len=new_len)
            except TypeError:
                button.draw()
        pgw.update(events)
        pg.display.update()

    def start(self) -> None:
        """
        Start the game loop and handle various events.
        """
        while not self.game_over:
            events: list[Event] = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.handle_quit_event()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.current_player_index:
                        continue
                    played_card: Optional[Card] = self.handle_mouse_button_down_event()
                    if played_card:
                        self.played_card = played_card
                        self.play_turn()
                elif event.type == pg.VIDEORESIZE:
                    self.handle_video_resize_event(event)
            if self.current_player_index:
                self.play_turn()
            self.render_game(events)
            if len(self.finished_players) == len(self.players) - 1:
                self._game_over = True

        pg.quit()

    def render_game_info(self) -> None:
        """
        Renders the game information on the screen.

        This method displays various game information such as penalty draw sum,
        required value, required suit, and total turns to skip if there are any.
        """
        padding: int = 10
        x: int = padding
        y: int = padding
        width: int
        height: int
        info_messages: list[str] = [
            "Penalty draw sum: ",
            "Required value: ",
            "Required suit: ",
            "Total turns to skip: ",
        ]
        info_values: list[Any] = [
            str(self.get_penalty) if self.get_penalty else None,
            self.game_params.get("value", None),
            self.game_params.get("suit", None),
            str(self.get_skip) if self.get_skip else None,
        ]
        info: zip[tuple[str, Optional[str]]] = zip(info_messages, info_values)
        for i, (message, param) in enumerate(info):
            if param:
                text: Surface = self.font.render(
                    message + param[0], True, self.text_color
                )
                width, height = text.get_size()
                field: Rect = Rect(x, y, width, height)
                pg.draw.rect(self.window, self.rect_bg_color, field)
                self.window.blit(text, (x, y))
                y += text.get_height() + padding

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
        texts: list[str] = [
            str(deck_len),
            "NEXT",
            "PENALTY",
            "MAKAO \nAND OUT",
            "MAKAO!",
        ]
        player: HumanPlayer = self.players[0]
        effects: list[Callable] = [
            partial(self.take_cards, player=player, number=1),
            partial(self.next_turn),
            partial(self.draw_penalty, player=player),
            partial(self.makao_out, player=player),
            partial(self.makao, player=player),
        ]
        inactive_color: tuple[int, int, int]
        hover_color: tuple[float, ...]
        for i, (message, effect) in enumerate(zip(texts, effects)):
            try:
                int(message)
                button_width = self.card_width
                button_height = self.card_height
                x = (
                    (self.window_width - button_width) // 2
                    + button_width
                    + 5
                    - self.card_width // 2
                )
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
                    onRelease=effect,
                )
            except ValueError:
                button_width = 90
                button_height = 50
                y = self.window_height - padding - button_height - (padding + button_height) * (i > 2)
                mul: int = (i - 2) if i > 2 else i
                x = self.window_width - padding - mul * button_width - (i - 1) % 2 * padding
                inactive_color = self.rect_bg_color
                hover_color = tuple(x * 0.85 for x in self.rect_bg_color)
                button = Button(
                    self.window,
                    x,
                    y,
                    button_width,
                    button_height,
                    text=message,
                    onRelease=effect,
                    inactiveColour=inactive_color,
                    hoverColour=hover_color,
                )
            self._game_rects["buttons"].append(button)

    def render_center_card(self) -> None:
        """
        Renders current center card and hidden deck of cards that player can draw from
        """
        card_image: Surface = image.load(self.center_card.get_image_name())
        x: int = (self.window_width - self.card_width) // 2 - self.card_width // 2
        y: int = (self.window_height - self.card_height) // 2
        self.window.blit(card_image, (x, y))

    def render_cards(
        self, player: Union[ComputerPlayer, HumanPlayer], all_visible: bool = False
    ) -> None:
        """
        Renders players cards based on their number:
            0 - Human, bottom, visible cards
            1 - Computer, left
            2 - Computer, top
            3 - Computer, right
        All computers' cards are rendered upside down

        :param player: Player object from list of players
        :raises WrongPosition: When wrong index is given
        """
        padding: int = 5
        position: int = self.players.index(player)
        up_down_players: list[int] = [0, 2]
        if not 0 <= position <= 3:
            raise WrongPosition(position)
        if player in self.finished_players:
            return

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

        if position in up_down_players:
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
                if position in up_down_players:
                    start_x = start_coord
                    y = y + (position - 1) * (card_height + padding)
                else:
                    start_y = start_coord
                    x = x - (position - 2) * (card_height + padding)

            if position in up_down_players:
                x = self._shift_coord(start_x, i, cards_per_row, card_width)
            else:
                y = self._shift_coord(start_y, i, cards_per_row, card_width)

            if all_visible:
                card_image = self._load_scale_image(
                    card_height, card_width, card.get_image_name()
                )
                if position_dict[position]["rotate"]:
                    card_image = pg.transform.rotate(card_image, 90)
            if position == 0:
                card_image = self._load_scale_image(
                    card_height, card_width, card.get_image_name()
                )
                card_rect: Rect = Rect(x, y, card_width, card_height)
                self._game_rects["human_cards"].append(card_rect)

            self.window.blit(card_image, (x, y))
        if position == self.current_player_index:
            turn_indicator_x: int
            turn_indicator_y: int

            if position in up_down_players:
                turn_indicator_x = self.window_width // 2
                turn_indicator_y = (
                    y + 15 * (position - 1) + card_height * (position // 2)
                )
            else:
                turn_indicator_x = (
                    x - 15 * (position - 2) + card_height * (position % 3)
                )
                turn_indicator_y = self.window_height // 2

            pg.draw.circle(
                self.window,
                self.rect_bg_color,
                (turn_indicator_x, turn_indicator_y),
                10,
            )

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
            1: {"start_coord": "y", "fixed_coord": padding, "rotate": True},
            2: {"start_coord": "x", "fixed_coord": padding, "rotate": False},
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
            card_image = pg.transform.smoothscale(card_image, (card_width, card_height))
        return card_image


if __name__ == "__main__":
    game = Game(4)
    game.start()
