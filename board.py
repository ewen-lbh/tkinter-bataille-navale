from tkinter import Place, Tk, Button, Frame, Label
from tkinter.constants import VERTICAL
from typing import Optional
from utils import *
from functools import partial
from ai import Strategy, NoStrategy
from random import randint

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

DESTROYER = 2
CRUISER = 3
SUBMARINE = 3
BATTLESHIP = 4
AIRCRAFT_CARRIER = 5

HORIZONTAL = 10
VERTICAL = 20


class Board:
    size: int
    cells: list[list[Button]]
    state: list[list[int]]
    game: "Game"
    owner: "Player"

    def __init__(
        self, game: "Game", grid_size: int, initial_state: int, owner: "Player"
    ):
        self.size = grid_size
        self.cells = []
        self.state = []
        self.mainframe = Frame(game.root)
        self.game = game
        self.owner = owner

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
    
    def vertical_coordinates(self, y: int, start_x: int, stop_x: int, step: int = 1) -> list[tuple[int, int]]:
        """
        Return a list of vertical coordinates, spanning from (start_x, y) to (stop_x, y).
        stop_x will be clamped to self.size - 1.
        """

        stop_x = min(stop_x, self.size - 1)
        return [(x, y) for x in range(start_x, stop_x, step)]

    def horizontal_coordinates(self, x: int, start_y: int, stop_y: int, step: int = 1) -> list[tuple[int, int]]:
        """
        Return a list of horizontal coordinates, spanning from (x, start_y) to (x, stop_y).
        stop_y will be clamped to self.size - 1.
        """

        stop_y = min(stop_y, self.size - 1)
        return [(x, y) for y in range(start_y, stop_y+1, step)]

    def cardinal_coordinates(
        self, x: int, y: int
    ) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
        """
        Given a center C at coordinates (x, y), it returns coordinates of N, S, W, E in:

                N
            W   C   E
                S
        """
        return (
            *self.horizontal_coordinates(x, y - 1, y + 1, 2),
            *self.vertical_coordinates(y, x - 1, x + 1, 2),
        )

def is_vertically_adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    d(f"adjacency check: {a,b=}", end=" ")
    xa, ya = a
    xb, yb = b
    is_adjacent = xa == xb and abs(ya - yb) == 1
    print(f"-> {is_adjacent}")
    return is_adjacent


def is_horizontally_adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return is_vertically_adjacent((a[1], a[0]), (b[1], b[0]))


class ControlledBoard(Board):
    """
    A board that is controlled by the player.
    Will be "locked" after the initial "hiding" phase,
    when the shooting phase starts.
    """

    locked: bool
    total_ships: int
    fleet: set[int]
    owner: "Player"

    def __init__(
        self,
        game: "Game",
        grid_size: int,
        fleet: set[int],
        owner: "Player" = None,
    ):
        super().__init__(game, grid_size, initial_state=WATER, owner=owner)
        self.fleet = fleet
        self.locked = False
        self.total_ships = sum(fleet)

    @property
    def ships_left(self) -> int:
        return max(self.total_ships - self.placed_ships, 0)

    @property
    def placed_ships(self) -> int:
        return sum(self @ (x, y) == SHIP for x, y in doublerange(self.size))

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

        self.change_cell(x, y, SUNKEN)
        return True

    def lock(self):
        self.locked = True

    @property
    def legal(self) -> bool:
        """
        Whether the current board's state is legal:
        The number of SHIP slots should exactly match the fleet
        """
        ships_found = 0
        for i, ship in enumerate(self.fleet):
            d(f"recherche du bateau #{i} (de taille {ship})")
            ship_found = False
            for (x, y) in doublerange(self.size):
                d(f"\tanalyse de la cellule {(x, y)}")
                if self @ (x, y) == WATER:
                    d(f"\tc'est de l'eau. cellule suivante...")
                    continue

                current_ship = ((x, y),)
                d(f"\tle bateau est maintenant {current_ship!r}")

                vertical_search_x = x
                d(f"\tVerticalement:")
                while len(current_ship) != ship:
                    vertical_search_x += 1
                    d(f"\t\tcellule ({vertical_search_x, y})")
                    if (
                        0 <= vertical_search_x <= self.size - 1
                        and self @ (vertical_search_x, y) == SHIP
                    ):
                        current_ship = (*current_ship, (vertical_search_x, y))
                        d(f"\t\tajoutée au bateau, qui est maintenant {current_ship}")
                    else:
                        d(f"\t\tc'est de l'eau. Fin de la recherche verticale.")
                        break

                horizontal_search_y = y
                d(f"\tHorizontalement:")
                while len(current_ship) != ship:
                    horizontal_search_y += 1
                    d(f"\t\tcellule ({x, horizontal_search_y})")
                    if (
                        0 <= horizontal_search_y <= self.size - 1
                        and self @ (x, horizontal_search_y) == SHIP
                    ):
                        current_ship = (*current_ship, (x, horizontal_search_y))
                        d(f"\t\t\tajoutée au bateau, qui est maintenant {current_ship}")
                    else:
                        d(f"\t\t\tc'est de leau.")
                        d(f"\t\tFin de la recherche horizontale.")
                        break

                if len(current_ship) == ship:
                    d(f"\t>> Le bateau a été trouvé!")
                    ship_found = True
                else:
                    d(f"\tLe bateau n'a pas été trouvé à partir de cette cellule.")
                    current_ship = ()

                if ship_found:
                    ships_found += 1
                    break
            if not ship_found:
                d(
                    f">> bateau #{i} non trouvé. le plateau n'est donc pas dans un état légal."
                )
                return False

        # check if there was as much ship slots as the total number of ships as dictated by the board's fleet
        return len(
            [(x, y) for (x, y) in doublerange(self.size) if self @ (x, y) == SHIP]
        ) == sum(self.fleet)


class ProjectiveBoard(Board):

    real_board: ControlledBoard
    shots_fired: int
    shots_missed: int
    owner: "Player"

    def __init__(
        self,
        game: "Game",
        grid_size: int,
        represents: ControlledBoard,
        owner: "Player" = None,
    ):
        super().__init__(game, grid_size, initial_state=UNKNOWN, owner=owner or represents.owner)
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
        self.owner.strategy.react_to_shot_result(x, y, hit_a_ship)

        board.change_cell(x, y, SUNKEN if hit_a_ship else WATER)
        board.shots_fired += 1
        if not hit_a_ship:
            board.shots_missed += 1

        board.game.end_turn()
