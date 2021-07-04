from tkinter import Label, StringVar, Tk, N, W, E, S, Widget
import tkinter
from tkinter.ttk import Frame, Button
from functools import partial
from typing import Any, Callable

# Constantes
SUNKEN = 2
OCCUPIED = 1
EMPTY = 0

STATE_NAMES = {
    SUNKEN: "⛝",
    OCCUPIED: "□",
    EMPTY: " ",
}


class Board:
    def __init__(self, title: str, grid_size: int):
        self.grid_size = grid_size
        self.cells = []

        self.root = Tk()
        self.root.title = title

        self.mainframe = Frame(self.root, width=self.grid_size*10, height=self.grid_size*10)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.hits_count = self.misses_count = 0

        for x in range(self.grid_size):
            self.cells.append([])
            for y in range(self.grid_size):
                cell = Button(self.mainframe, text=f"{x}:{y}")
                cell.bind('<Button-1>', partial(self.handle, self.switch_occupied_empty, x, y))
                cell.bind('<Button-3>', partial(self.handle, self.hit, x, y))
                self.cells[x].append(cell)
                cell.grid(row=x, column=y)
        
        Label(self.mainframe, textvariable=StringVar(value=0))


    def __matmul__(self, new_state):
        """
        Sets the entire board's state to the one given.
        A state is represented as a 2D array of state integers (see Démineur.change_cell)
        """
        for x, y in doublerange(self.grid_size):
            self.change_cell(x, y, new_state[x][y])
    
    def handle(self,  method: Callable[[int, int], Any], x: int, y: int, _: tkinter.Event,) -> Any:
        """
        Used to bind events with tkinter's .bind()
        Usage: 
        ```python
        <thing>.bind('<mapping>', partial(self.handle, self.<method to bind>, x, y))
        ```
        """
        return method(x, y)
        
    
    def change_cell(self, x:int, y:int, state: int):
        """
        Sets the state of the specified cell.
        A state is represented as an integer:
        - 2 (or SUNKEN) represents a sunken spot
        - 1 (or OCCUPIED) represents a boat spot
        - 0 (or EMPTY) represents a water spot
        """
        self.cells[x][y].configure(text=STATE_NAMES[state])
    
    def switch_occupied_empty(self, x:int, y:int):
        self.change_cell(x, y, OCCUPIED if self.state_of(x, y) == EMPTY else EMPTY)
    
    def hit(self, x: int, y: int) -> bool:
        """
        Returns whether it hit a non-sunken boat or not
        """
        self.hits_count += 1
        if self.state_of(x, y) == OCCUPIED:
            self.change_cell(x, y, SUNKEN)
            return True
        else:
            self.misses_count += 1
            return False

    @property
    def state(self) -> list[list[int]]:
        state_repr = [[EMPTY] * self.grid_size] * self.grid_size
        for x, y in doublerange(self.grid_size):
            state_repr[x][y] = self.state_of(x, y)
        return state_repr
    
    def state_of(self, x:int, y:int) -> int:
        return {v:k for k,v in STATE_NAMES.items()}[self.cells[x][y]['text']]

    @property
    def won(self) -> bool:
        return not any(cell_state == OCCUPIED for cell_state in self.state)
    
    @property
    def accuracy(self) -> float:
        try:
            return (self.hits_count - self.misses_count) / self.hits_count
        except ZeroDivisionError:
            return 0

    def __call__(self, initial_state=None):
        self @ (initial_state or [[EMPTY] * self.grid_size] * self.grid_size)
        self.root.mainloop()


def doublerange(outer, inner=None):
    if inner is None:
        inner = outer
    for a in range(outer):
        for b in range(inner):
            yield a, b


if __name__ == "__main__":
    démineur = Board(title="Démineur", grid_size=10)
    démineur()
