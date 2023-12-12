SYMBOLS: list[str] = ["clubs", "spades", "diamonds", "hearts"]
VALUES: list[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SYMBOLS_UTF_VAL: dict[str, str] = {
    "clubs": "\u2663",
    "spades": "\u2660",
    "diamonds": "\u2666",
    "hearts": "\u2665",
}
SYMBOLS_COLORS: dict[str, str] = {
    "clubs": "black",
    "spades": "black",
    "diamonds": "red",
    "hearts": "red"
}
COLOR_TO_ANSI: dict[str, str] = {
    "black": "\033[97m",
    "black": "\033[97m",
    "red": "\033[31m",
    "red": "\033[31m",
    "reset": "\033[0m"
}
