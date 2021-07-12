from functools import partial
from tkinter import Tk
from tkinter.ttk import Button, Frame
from utils import *

# Constantes
SUNKEN = 2  # Coulé
SHIP = 1  # Occupé (case avec un bateau non coulé, pour les ControlledBoards seulement)
WATER = 0  # Eau (case vide)
UNKNOWN = 3  # Pour les ProjectiveBoards seulement

# Les états à afficher par rapport à leur code
CELL_DISPLAY_STATES = {
    SUNKEN: {"text": "⛝", "color": "red"},
    SHIP: {"text": "□", "color": "white"},
    WATER: {"text": "≋", "color": "blue"},
    UNKNOWN: {"text": " ", "color": "grey"},
}


class Board:

    grid_size: int
    cells: list[list[Button]]

    def __init__(self, root: Tk, grid_size: int, initial_state: int):
        self.grid_size = grid_size
        self.cells = []
        self.mainframe = Frame(root)

        for x in range(self.grid_size):
            self.cells.append([])
            for y in range(self.grid_size):
                cell = Button(self.mainframe, text=f"{x}:{y}")
                cell.bind("<Button-1>", partial(handle, self.handle_cell_Button1, x, y))
                cell.bind("<Button-3>", partial(handle, self.handle_cell_Button3, x, y))
                self.cells[x].append(cell)
                cell.grid(row=x, column=y)

        self.set_state([[initial_state] * grid_size] * grid_size)

    def __matmul__(self, coords):
        """aesthetics: @ (x, y) to get cell state at (x, y)"""
        return self.state[coords[0]][coords[1]]

    def handle_cell_Button1(self, x: int, y: int):
        pass

    def handle_cell_Button3(self, x: int, y: int):
        pass

    def set_state(self, new_state):
        """
        Sets the entire board's state to the one given.
        A state is represented as a 2D array of state integers (see Démineur.change_cell)
        """
        for x, y in doublerange(self.grid_size):
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

    @property
    def state(self) -> list[list[int]]:
        """
        Get state of cells as 2D array
        """
        state_repr = [[WATER] * self.grid_size] * self.grid_size
        for x, y in doublerange(self.grid_size):
            state_repr[x][y] = self.state_of(x, y)
        return state_repr

    def state_of(self, x: int, y: int) -> int:
        """
        Get state of cell at row x column y
        """
        return {v: k for k, v in CELL_DISPLAY_STATES.items()}[self.cells[x][y]["text"]]

    def render(self, column: int, row: int):
        self.mainframe.grid(column=column, row=row)


class ControlledBoard(Board):
    """
    A board that is controlled by the player.
    Will be "locked" after the initial "hiding" phase,
    when the shooting phase starts.
    """

    locked: bool

    def __init__(self, root: Tk, grid_size: int):
        super().__init__(root, grid_size, WATER)
        self.locked = False

        self.handle_cell_Button1 = self.place_or_remove

    def __xor__(self, coords):
        """aesthetics: ^ (x, y) to fire at (x, y)"""
        return self.fire(*coords)

    def place_or_remove(self, x: int, y: int):
        """
        Switches between placing and removing a ship at row x column y.
        """
        self.change_cell(x, y, SHIP if self.state_of(x, y) == WATER else WATER)

    def fire(self, x: int, y: int) -> bool:
        """
        Fires a shot at row x column y.
        Returns whether the shot hit a non-sunken ship or not
        """
        self.hits_count += 1
        if self.state_of(x, y) == SHIP:
            self.change_cell(x, y, SUNKEN)
            return True
        else:
            self.misses_count += 1
            return False

    def lock(self):
        self.locked = True

    @property
    def won(self) -> bool:
        """
        Whether all the ships sank
        """
        return not any(cell_state == SHIP for cell_state in self.state)

    @property
    def accuracy(self) -> float:
        """
        Proportion of shots taken that hit a ship
        """
        try:
            return (self.hits_count - self.misses_count) / self.hits_count
        except ZeroDivisionError:
            return 0


class ProjectiveBoard(Board):

    real_board: ControlledBoard

    def __init__(self, root: Tk, grid_size: int, represents: ControlledBoard):
        super().__init__(root, grid_size, UNKNOWN)
        self.real_board = represents

        self.handle_cell_Button1 = self.fire

    def __xor__(self, coords):
        """aesthetics: ^ (x, y) to fire at (x, y)"""
        return self.fire(*coords)

    def fire(board, x: int, y: int) -> None:
        # Don't fire if the cell is already known (i.e. has already been shot)
        if (board @ (x, y)) != UNKNOWN:
            return

        hit_a_ship = board.real_board ^ (x, y)

        board.change_cell(x, y, SUNKEN if hit_a_ship else WATER)


class Player:
    own_board: ControlledBoard
    ennemy_board: ProjectiveBoard
    hits: int
    misses: int

    def __init__(
        self, root: Tk, board: ControlledBoard, ennemy_board: ControlledBoard
    ) -> None:
        if board.grid_size == ennemy_board.grid_size:
            raise TypeError("The two boards should have the same size")

        self.own_board = board
        self.ennemy_board = ProjectiveBoard(
            root, board.grid_size, represents=ennemy_board
        )


class HumanPlayer(Player):
    def __init__(
        self, root: Tk, board: ControlledBoard, ennemy_board: ControlledBoard
    ) -> None:
        super().__init__(root, board, ennemy_board)

    def render_boards(self):
        self.own_board.render(0, 1)
        self.ennemy_board.render(0, 0)


class AIPlayer(Player):
    def __init__(
        self, root: Tk, board: ControlledBoard, ennemy_board: ControlledBoard
    ) -> None:
        super().__init__(root, board, ennemy_board)


if __name__ == "__main__":
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    user_board = ControlledBoard(root, grid_size=10)
    bot_board = ControlledBoard(root, grid_size=10)

    user = Player(root, user_board, ennemy_board=bot_board)
    bot = AIPlayer(root, bot_board, ennemy_board=user_board)

    root.mainloop()
