# Damian D'Souza - Macao project

## Table of Contents

- [Name](#name)
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Name
Macao

## Description

Macao is a popular card game, this project is based on its Polish rules. The game is played with a standard deck of 52 cards and can be played by 2 to 4 players. The objective of the game is to be the first player to get rid of all your cards.

Each player is dealt five cards at the start of the game. The remaining cards form the draw pile, with the top card turned face up to start the discard pile. Players take turns playing a card that matches the rank or suit of the top card of the discard pile. If a player cannot play a card, they must draw a card from the draw pile. If the player can play the drawn card, they may do so, otherwise, they must keep the card and end their turn. Functional cards (2, 3, 4, W, D, K, A) have special effects, which are described below.

 - **2♠ 2♥ 2♣ 2◆ 3♠ 3♥ 3♣ 3◆**: the next player draws two/three cards (depending on the number of pips). In the case where the next player also has a two/three, they can lay it down, thus forcing the subsequent player to pick up the sum of the values of the cards (where the next player can also play a two/three, and so on). In the worst-case scenario, a player might have to draw 29 cards (four twos [8 cards] + four threes [12 cards] + 3 jokers for threes [9 cards]).

- **4♠ 4♥ 4♣ 4◆**: the next player skips one turn. To defend against this, you must play another four, then the number of skipped turns accumulates and affects the next player in line. Functional cards do not work on a blocked player (the effect is applied to the next player in line).

- **W♠ W♥ W♣ W◆**: the player can request cards based on their face value (only non-functional cards). It is not allowed to play a queen using the rule "queen for everything, everything for the queen." The request for a specific card by a jack applies for the entire subsequent turn (including the player who played the jack) and can only be changed by playing another jack (overriding the request to a different card or not requesting any card).

- **D♠ D♥ D♣ D◆**: the "queen for everything, everything for the queen" rule means the possibility of laying down a queen on any card, regardless of color and value (sometimes: unless the card prevents it because it is functional) and placing any card on a laid queen. Additionally, in some versions, the rule D♠ (or also D♥) applies, preventing the action of biting kings or all functional cards.

- **K♥ K♠**: these are two kings that cause the previous (**K♠**) or next (**K♥**) player to draw five cards, depending on the color of that king. To defend against such a king, you must play another king (the cards add up, resulting in the attacker drawing 10 cards), and **K♥ K♠** can be blocked by non-biting kings **K♣ K◆**.

- **A♠ A♥ A♣ A◆**: the player can demand a change of color (changing the color by an ace affects the next player, not the entire queue of players, as in the case of a jack). Sometimes, you can defend against this by laying down more than one card of the same value, for example, three fives (the last logically being of a different color) or laying down another ace and changing the color to a different one. In some variants, this rule does not apply to queens.

The game continues until a player has no cards left. For more detailed rules, please refer to the [Polish Wikipedia page](https://pl.wikipedia.org/wiki/Makao_(gra_karciana)).

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
1. Clone the repository: `git clone https://gitlab-stud.elka.pw.edu.pl/ddsouza/makao-projekt-pipr-damian-dsouza`
2. Navigate to the project directory: `cd makao-projekt-pipr-damian-dsouza`
3. Create a venv and activate it:
    - Linux:
        - `python3 -m venv .venv`
        - `source venv/bin/activate`
    - Windows:
        - `python -m venv .venv`
        - `venv\Scripts\activate`
4. Install the required packages: `pip install -r requirements.txt`

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
