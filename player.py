from board import ControlledBoard, ProjectiveBoard, SUNKEN, WATER
from utils import *
from main import Game, PLACING, SHOOTING
from typing import Any, Optional
from tkinter import Button


class Player:
    own_board: ControlledBoard
    ennemy_board: ProjectiveBoard
    ok_button: Button
    game: Game
    index: int
    selected_coordinates: tuple[int, int]
    name: str

    def __init__(
        self,
        game: Game,
        board: ControlledBoard,
        ennemy_board: ControlledBoard,
        index: int,
        name: str,
    ) -> None:
        if board.size != ennemy_board.size:
            raise TypeError("The two boards should have the same size")

        self.game = game
        self.index = index
        self.name = name

        self.own_board = board
        self.ennemy_board = ProjectiveBoard(game, board.size, represents=ennemy_board)
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

    def is_it_my_turn(self) -> bool:
        return self.index == self.game.current_player_index


class HumanPlayer(Player):
    def __init__(
        self,
        game: Game,
        board: ControlledBoard,
        ennemy_board: ControlledBoard,
        index: int,
        name: str,
    ) -> None:
        super().__init__(game, board, ennemy_board, index, name)

    def render(self):
        self.own_board.render(0, 1)
        self.ennemy_board.render(0, 0)
        self.ok_button.grid(column=1, row=1)

    def handle_click_ok(self, event) -> Any:
        if self.game.phase == PLACING:
            d(f"handling OK button click: locking board, switching to shooting phase")
            self.own_board.lock()
            self.game.phase = SHOOTING


class AIPlayer(Player):
    def __init__(
        self,
        game: Game,
        board: ControlledBoard,
        ennemy_board: ControlledBoard,
        index: int,
        name: str,
    ) -> None:
        super().__init__(game, board, ennemy_board, index, name=f"[AI] {name}")

    def decide_coordinate(self) -> tuple[int, int]:
        """
        Decide coordinates where to shoot.
        """
        return self.ennemy_board.random_coordinates()

    def place_ships(self) -> None:
        """
        Fill own board with ship spots
        """
        while self.own_board.ships_left:
            self.own_board.place_or_remove(*self.own_board.random_coordinates())
