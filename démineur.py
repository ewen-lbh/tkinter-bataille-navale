import tkinter
from functools import partial
from tkinter import Label, StringVar, Tk
from tkinter.ttk import Button, Frame
from typing import Any, Callable

# Constantes
SUNKEN = 2  # Coulé
SHIP = 1  # Occupé (case avec un bateau non coulé)
WATER = 0  # Eau (case vide)

# Les états à afficher par rapport à leur code
CELL_DISPLAY_STATES = {
    SUNKEN: "⛝",
    SHIP: "□",
    WATER: " ",
}


class Board:
    def __init__(self, root: Tk, grid_size: int):
        self.grid_size = grid_size
        self.cells = []

        self.mainframe = Frame(root)

        self.hits_count = self.misses_count = 0

        for x in range(self.grid_size):
            self.cells.append([])
            for y in range(self.grid_size):
                cell = Button(self.mainframe, text=f"{x}:{y}")
                cell.bind(
                    "<Button-1>", partial(self.handle, self.place_or_remove, x, y)
                )
                cell.bind("<Button-3>", partial(self.handle, self.hit, x, y))
                self.cells[x].append(cell)
                cell.grid(row=x, column=y)

        self @ ([[WATER] * self.grid_size] * self.grid_size)

    def __matmul__(self, new_state):
        """
        Sets the entire board's state to the one given.
        A state is represented as a 2D array of state integers (see Démineur.change_cell)
        """
        for x, y in doublerange(self.grid_size):
            self.change_cell(x, y, new_state[x][y])

    def handle(
        self,
        method: Callable[[int, int], Any],
        x: int,
        y: int,
        _: tkinter.Event,
    ) -> Any:
        """
        Used to bind events with tkinter's .bind()
        Usage:
        ```python
        <thing>.bind('<mapping>', partial(self.handle, self.<method to bind>, x, y))
        ```
        """
        return method(x, y)

    def change_cell(self, x: int, y: int, state: int):
        """
        Sets the state of the specified cell at row x column y.
        A state is represented as an integer:
        - 2 (or SUNKEN) represents a sunken spot
        - 1 (or SHIP) represents a ship spot
        - 0 (or WATER) represents a water (empty) spot
        """
        self.cells[x][y].configure(text=CELL_DISPLAY_STATES[state])

    def place_or_remove(self, x: int, y: int):
        """
        Switches between placing and removing a ship at row x column y.
        """
        self.change_cell(x, y, SHIP if self.state_of(x, y) == WATER else WATER)

    def hit(self, x: int, y: int) -> bool:
        """
        Fires a shot at row x column y
        Returns whether the shot hit a non-sunken ship or not
        """
        self.hits_count += 1
        if self.state_of(x, y) == SHIP:
            self.change_cell(x, y, SUNKEN)
            return True
        else:
            self.misses_count += 1
            return False

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


def doublerange(outer, inner=None):
    if inner is None:
        inner = outer
    for a in range(outer):
        for b in range(inner):
            yield a, b


if __name__ == "__main__":
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    player_board = Board(root, grid_size=10)
    ennemy_board = Board(root, grid_size=10)
    player_board.mainframe.grid(column=0, row=1)
    ennemy_board.mainframe.grid(column=0, row=0)
    root.mainloop()
