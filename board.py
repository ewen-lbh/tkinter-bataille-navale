from main import Game
from tkinter import Tk, Button, Frame, Label
from typing import Optional
from utils import *
from functools import partial

# Constantes
WATER = 0  # Eau (case vide)
SHIP = 1  # Occupé (case avec un bateau non coulé, pour les ControlledBoards seulement)
SUNKEN = 2  # Coulé
UNKNOWN = 3  # Pour les ProjectiveBoards seulement

# Les états à afficher par rapport à leur code
CELL_DISPLAY_STATES = {
    SUNKEN: {"text": "⛝", "bg": "red"},
    SHIP: {"text": "□", "bg": "white"},
    WATER: {"text": "≋", "bg": "blue"},
    UNKNOWN: {"text": "?", "bg": "grey"},
}


class Board:
    size: int
    cells: list[list[Button]]
    state: list[list[int]]
    game: Game

    def __init__(self, game: Game, grid_size: int, initial_state: int):
        self.size = grid_size
        self.cells = []
        self.state = []
        self.mainframe = Frame(game.root)
        self.game = game

        for x in range(self.size):
            self.cells.append([])
            self.state.append([])
            for y in range(self.size):
                cell = Button(self.mainframe, text=f"{x}:{y}")
                cell.bind("<Button-1>", partial(handle, self.handle_cell_Button1, x, y))
                cell.bind("<Button-3>", partial(handle, self.handle_cell_Button3, x, y))
                self.cells[x].append(cell)
                self.state[x].append(initial_state)
                self.change_cell(x, y, initial_state)
                cell.grid(row=x, column=y)

    def __matmul__(self, coords):
        """aesthetics: @ (x, y) to get cell state at (x, y)"""
        return self.state[coords[0]][coords[1]]

    def handle_cell_Button1(self, x: int, y: int):
        d(f"handling <Button 1> {x=}, {y=}")

    def handle_cell_Button3(self, x: int, y: int):
        d(f"handling <Button 3> {x=}, {y=}")

    def set_state(self, new_state):
        """
        Sets the entire board's state to the one given.
        A state is represented as a 2D array of state integers (see Démineur.change_cell)
        """
        for x, y in doublerange(self.size):
            self.change_cell(x, y, new_state[x][y])

    def change_cell(self, x: int, y: int, state: int):
        """
        Sets the state of the specified cell at row x column y.
        A state is represented as an integer:
        - 2 (or SUNKEN) represents a sunken spot
        - 1 (or SHIP) represents a ship spot (for ControlledBoards)
        - 0 (or WATER) represents a water (empty) spot
        - 3 (or UNKNOWN) represents a unknown spot (for ProjectiveBoards)
        """
        self.cells[x][y].configure(**CELL_DISPLAY_STATES[state])
        self.state[x][y] = state

    def state_of(self, x: int, y: int) -> int:
        """
        Get state of cell at row x column y
        """
        return dict_reciprocal(CELL_DISPLAY_STATES, key=lambda s: s["text"])[
            self.cells[x][y]["text"]
        ]

    def render(self, column: int, row: int):
        self.mainframe.grid(column=column, row=row)

    def random_coordinates(self) -> tuple[int, int]:
        return randint(0, self.size - 1), randint(0, self.size - 1)


class ControlledBoard(Board):
    """
    A board that is controlled by the player.
    Will be "locked" after the initial "hiding" phase,
    when the shooting phase starts.
    """

    locked: bool
    total_ships: int

    def __init__(self, game: Game, grid_size: int, ships: int):
        super().__init__(game, grid_size, WATER)
        self.locked = False
        self.total_ships = ships

    @property
    def ships_left(self) -> int:
        return max(self.total_ships - self.placed_ships, 0)

    @property
    def placed_ships(self) -> int:
        placed_ships = 0
        for x, y in doublerange(self.size):
            if self @ (x, y) == SHIP:
                placed_ships += 1
        return placed_ships

    def handle_cell_Button1(self, x, y):
        super().handle_cell_Button1(x, y)
        self.place_or_remove(x, y)

    def __xor__(self, coords):
        """aesthetics: ^ (x, y) to fire at (x, y)"""
        return self.fire(*coords)

    def place_or_remove(self, x: int, y: int):
        """
        Switches between placing and removing a ship at row x column y.
        """
        if self.locked:
            d(f"board is locked, not switching state of ({x}, {y})")
            return
        if not self.ships_left and self @ (x, y) == WATER:
            d(f"no ships left!")
            return
        if self @ (x, y) == WATER:
            d(f"{self.ships_left=}, changing state of ({x}, {y}) to SHIP")
            self.change_cell(x, y, SHIP)
        else:
            d(f"{self.ships_left=}, changing state of ({x}, {y}) to WATER")
            self.change_cell(x, y, WATER)

    def fire(self, x: int, y: int) -> bool:
        """
        Fires a shot at row x column y.
        Returns whether the shot hit a non-sunken ship or not
        """
        if self.state_of(x, y) == WATER:
            return False
        else:
            self.change_cell(x, y, SUNKEN)
            return True

    def lock(self):
        self.locked = True


class ProjectiveBoard(Board):

    real_board: ControlledBoard
    shots_fired: int
    shots_missed: int

    def __init__(self, game: Game, grid_size: int, represents: ControlledBoard):
        super().__init__(game, grid_size, UNKNOWN)
        self.real_board = represents
        self.shots_missed = 0
        self.shots_fired = 0

    def handle_cell_Button1(self, x, y):
        super().handle_cell_Button1(x, y)
        self.fire(x, y)

    def __xor__(self, coords):
        """aesthetics: ^ (x, y) to fire at (x, y)"""
        return self.fire(*coords)

    def fire(board, x: int, y: int) -> None:
        d(f"fire at {x=}, {y=}.")
        # # Don't fire if the cell is already known (i.e. has already been shot)
        # if (board @ (x, y)) != UNKNOWN:
        #     d(f"state={board @ (x, y)} is already known, not firing.")
        #     return

        hit_a_ship = board.real_board.fire(x, y)
        d(f"fired, {hit_a_ship=}, changing cell state")

        board.change_cell(x, y, SUNKEN if hit_a_ship else WATER)
        board.shots_fired += 1
        if not hit_a_ship:
            board.shots_missed += 1

        board.game.end_turn()
