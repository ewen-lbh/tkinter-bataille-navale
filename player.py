from ai import NoStrategy, Strategy
from tkinter.constants import VERTICAL
from board import (
    ControlledBoard,
    HORIZONTAL,
    ProjectiveBoard,
    SUNKEN,
    WATER,
)
from utils import *
from typing import Any, Optional, Type
from tkinter import Button
import random


# Constantes
PLACING = 4
SHOOTING = 5
DECIDING = 6


class Player:
    own_board: ControlledBoard
    ennemy_board: ProjectiveBoard
    ok_button: Button
    game: "Game"
    index: int
    selected_coordinates: tuple[int, int]
    strategy: Strategy
    name: str

    def __init__(
        self,
        game: "Game",
        board: ControlledBoard,
        ennemy_board: ControlledBoard,
        index: int,
        name: str,
        strategy: Type[Strategy],
    ) -> None:
        if board.size != ennemy_board.size:
            raise TypeError("The two boards should have the same size")

        self.game = game
        self.index = index
        self.name = name
        self.own_board = board
        self.own_board.owner = self
        self.ennemy_board = ProjectiveBoard(
            game, board.size, represents=ennemy_board, owner=self
        )
        self.strategy = strategy(strategy.name, self.own_board, self.ennemy_board)
        self.ok_button = Button(text="OK")
        self.ok_button.bind("<Button 1>", self.handle_click_ok)

    def handle_click_ok(self, event) -> Any:
        """
        Handles a click on the OK button
        """
        raise NotImplementedError("Please implement handle_click_ok.")

    @property
    def accuracy(self) -> Optional[float]:
        """
        Proportion of shots fired that hit a ship.
        None if no shots have been fired.
        """
        try:
            return (
                self.ennemy_board.shots_fired - self.ennemy_board.shots_missed
            ) / self.ennemy_board.shots_fired
        except ZeroDivisionError:
            return None

    @property
    def won(self) -> bool:
        """
        Returns True if none the cell's of the ennemy's (controlled) board are ships (i.e. all are sunken or water)
        """
        return all(
            self.ennemy_board.real_board @ (x, y) in (SUNKEN, WATER)
            for x, y in doublerange(self.ennemy_board.size)
        )

    def turn_is_mine(self) -> bool:
        return self.index == self.game.current_player_index

    @property
    def human(self) -> bool:
        raise NotImplementedError("Please implement human property")

    def d(self, t: str, *args, **kwargs):
        return d(
            ("[green]" if self.human else "[cyan]") + self.name + "[/] " + t,
            *args,
            **kwargs,
        )


class HumanPlayer(Player):
    def __init__(
        self,
        game: "Game",
        board: ControlledBoard,
        ennemy_board: ControlledBoard,
        index: int,
        name: str,
    ) -> None:
        super().__init__(game, board, ennemy_board, index, name, strategy=NoStrategy)

    def render(self):
        self.own_board.render(0, 1)
        self.ennemy_board.render(0, 0)
        self.ok_button.grid(column=1, row=1)

    def handle_click_ok(self, event) -> Any:
        if self.game.phase == PLACING:
            self.d(
                f"handling OK button click: locking board, switching to shooting phase"
            )
            if not self.own_board.legal:
                self.d(f"board is not legal! not locking & switching phase.")
                return
            self.own_board.lock()
            self.game.phase = SHOOTING

    @property
    def human(self) -> bool:
        return True


class AIPlayer(Player):
    def __init__(
        self,
        game: "Game",
        board: ControlledBoard,
        ennemy_board: ControlledBoard,
        strategy: Type[Strategy],
        index: int,
        name: str,
    ) -> None:
        super().__init__(
            game, board, ennemy_board, index, name=f"[AI] {name}", strategy=strategy
        )

    def decide_coordinates(self) -> tuple[int, int]:
        """
        Decide coordinates where to shoot.
        """
        return self.strategy.choose_shot_location()

    def place_ships(self) -> None:
        """
        Fill own board with ship spots
        """
        for ship in self.own_board.fleet:
            self.place_ship_randomly(ship)

    def place_ship(self, coords: list[tuple[int, int]]) -> None:
        for (x, y) in coords:
            self.own_board.place_or_remove(x, y)

    def can_place_ship_at(self, x: int, y: int, ship: int, orientation: int):
        """
        Returns whether placing a ship at (x, y) in orientation `orientation` (`VERTICAL` or `HORIZONTAL`)
        is possible.
        """
        if orientation == HORIZONTAL:
            return [
                self.own_board @ (x, y)
                for (x, y) in self.own_board.horizontal_coordinates(x, y, y + ship)
            ] == [WATER] * ship
        elif orientation == VERTICAL:
            return [
                self.own_board @ (x, y)
                for (x, y) in self.own_board.vertical_coordinates(y, x, x + ship)
            ] == [WATER] * ship
        else:
            raise ValueError(f"Unknown orientation {orientation!r}")

    def place_ship_randomly(self, ship: int) -> None:
        """
        Returns an available spot for a ship of length `ship`.
        Raises ValueError if the board does not have room for one.
        """

        coords = list(doublerange(self.own_board.size))
        random.shuffle(coords)
        for (x, y) in coords:
            if self.can_place_ship_at(x, y, ship, VERTICAL):
                self.place_ship(self.own_board.vertical_coordinates(y, x, x + ship))
                return
            elif self.can_place_ship_at(x, y, ship, HORIZONTAL):
                self.place_ship(self.own_board.horizontal_coordinates(x, y, y + ship))
                return
        raise ValueError(f"Cannot fit a {ship}-cell-long ship in this player's board")

    @property
    def human(self) -> bool:
        return False
