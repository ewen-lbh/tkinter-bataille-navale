from tkinter import Tk, N, W, E, S
from tkinter.ttk import Frame, Button

# Constantes
SUNKEN = 2
OCCUPIED = 1
EMPTY = 0

STATE_NAMES = {
    SUNKEN: "⛝",
    OCCUPIED: "□",
    EMPTY: "",
}


class Démineur:
    def __init__(self, title: str, grid_size: int):
        self.grid_size = grid_size
        self.cells = [[]] * grid_size

        self.root = Tk()
        self.root.title = title

        self.mainframe = Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.root.columnconfigure(0)
        self.root.rowconfigure(0)

        for x, y in doublerange(grid_size):
            cell = Button(self.mainframe, text=f"{x}:{y}")
            self.cells[x].append(cell)
            cell.grid(row=x, column=y)


    def __matmul__(self, new_state):
        """
        Sets the state to the one given.
        A state is represented as a 2D array of integers:
        - 2 (or SUNKEN) represents a sunken spot
        - 1 (or OCCUPIED) represents a boat spot
        - 0 (or EMPTY) represents a water spot
        """
        for x, y in doublerange(self.grid_size):
            self.cells[x][y].configure(text=STATE_NAMES[new_state[x][y]])

    @property
    def state(self) -> list[list[int]]:
        for x, y in doublerange(self.grid_size):
            self.cells[x][y]
            pass

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
    démineur = Démineur(title="Démineur", grid_size=10)
    print(démineur.cells[0][0].keys())
    démineur()

