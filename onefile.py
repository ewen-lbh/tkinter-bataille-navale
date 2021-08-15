import random
import tkinter
from functools import partial
from random import randint
from tkinter import Button, Frame, Label, Place, StringVar, Tk
from tkinter.constants import VERTICAL
from typing import *

try:
    from rich import print
    from rich import print as pprint
except ImportError:
    from pprint import pprint

## Utils

def handle(
    method: Callable[[int, int], Any],
    x: int,
    y: int,
    _: tkinter.Event,
) -> Any:
    """
    Used to bind events with tkinter's .bind()
    Usage:
    ```python
    <thing>.bind('<mapping>', partial(self.handle, self.<method to bind>, x, y)) ```
    """
    return method(x, y)


K, V, H = TypeVar("K"), TypeVar("T"), TypeVar("Hashable_V")


def dict_reciprocal(o, key: Callable[[V], H] = lambda x: x) :
    return {key(v): k for k, v in o.items()}


def doublerange(outer, inner=None):
    """
    inner defaults to outer's value
    """
    if inner is None:
        inner = outer
    for a in range(outer):
        for b in range(inner):
            yield a, b


def d(text: str, *args, **kwargs):
    print("[dim]\[debug][/] " + text, *args, **kwargs)


def french_join(elements: Union[list, tuple]) -> str:
    return ", ".join(map(str, elements[:-1])) + " et " + str(elements[-1])
## Board

# Constantes
WATER = 0  # Eau (case vide)
SHIP = 1  # Occupé (case avec un bateau non coulé, pour les ControlledBoards seulement)
SUNKEN = 2  # Coulé
UNKNOWN = 3  # Pour les ProjectiveBoards seulement
MISSED = 4 # Case d'eau mais touchée

# Les états à afficher par rapport à leur code
CELL_DISPLAY_STATES = {
    SUNKEN: {"text": "T️", "bg": "red"}, # T comme touché
    SHIP: {"text": "B", "bg": "white"}, # B comme bateau
    WATER: {"text": "E", "bg": "blue"}, # E comme eau
    MISSED: {"text": "M", "bg": "cyan"}, # M comme manqué
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
    game: "Game"
    owner: "Player"
    locked: bool

    def __init__(
        self, game: "Game", grid_size: int, initial_state: int, owner: "Player"
    ):
        self.size = grid_size
        self.cells = []
        self.state = []
        self.mainframe = Frame(game.root)
        self.game = game
        self.owner = owner
        self.locked = False

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
        self.d(f"handling <Button 1> x={x}, y={y}")

    def handle_cell_Button3(self, x: int, y: int):
        self.d(f"handling <Button 3> x={x}, y={y}")

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
    
    def within_bounds(self, x: int, y: int) -> bool:
        """
        Check if the cell's coordinates are within bounds of the board
        """
        return 0 <= x <= self.size and 0 <= y <= self.size

    def render(self, column: int, row: int, span: int = 1):
        self.mainframe.grid(column=column, row=row, columnspan=span, rowspan=span)

    def random_coordinates(self) :
        return randint(0, self.size - 1), randint(0, self.size - 1)

    def vertical_coordinates(
        self, y: int, start_x: int, stop_x: int, step: int = 1
    ):
        """
        Return a list of vertical coordinates, spanning from (start_x, y) to (stop_x, y).
        stop_x will be clamped to self.size - 1.
        """

        stop_x = min(stop_x, self.size - 1)
        return [(x, y) for x in range(start_x, stop_x, step)]

    def horizontal_coordinates(
        self, x: int, start_y: int, stop_y: int, step: int = 1
    ):
        """
        Return a list of horizontal coordinates, spanning from (x, start_y) to (x, stop_y).
        stop_y will be clamped to self.size - 1.
        """

        stop_y = min(stop_y, self.size - 1)
        return [(x, y) for y in range(start_y, stop_y + 1, step)]

    def cardinal_coordinates(
        self, x: int, y: int
    ):
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

    def d(self, t: str, *args, **kwargs):
        if self.owner is None:
            return d(t, *args, **kwargs)
        return d(
            ("[green]" if self.owner.human else "[cyan]")
            + self.owner.name
            + "[/] "
            + t,
            *args,
            **kwargs,
        )

    def lock(self):
        self.locked = True


class ControlledBoard(Board):
    """
    A board that is controlled by the player.
    Will be "locked" after the initial "hiding" phase,
    when the shooting phase starts.
    """

    total_ships: int
    owner: "Player"

    def __init__(
        self,
        game: "Game",
        grid_size: int,
        fleet,
        owner: "Player" = None,
    ):
        super().__init__(game, grid_size, initial_state=WATER, owner=owner)
        self.fleet = fleet
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
            self.d(f"board is locked, not switching state of ({x}, {y})")
            return
        if not self.ships_left and self @ (x, y) == WATER:
            self.d(f"no ships left!")
            return
        if self @ (x, y) == WATER:
            self.d(f"self.ships_left={self.ships_left}, changing state of ({x}, {y}) to SHIP")
            self.change_cell(x, y, SHIP)
        else:
            self.d(f"self.ships_left={self.ships_left}, changing state of ({x}, {y}) to WATER")
            self.change_cell(x, y, WATER)

    def fire(self, x: int, y: int) -> bool:
        """
        Fires a shot at row x column y.
        Returns whether the shot hit a non-sunken ship or not
        """
        if self.state_of(x, y) in (WATER, MISSED):
            self.change_cell(x, y, MISSED)
            return False

        self.change_cell(x, y, SUNKEN)
        return True

    @property
    def legal(self) -> bool:
        """
        Whether the current board's state is legal:
        The number of SHIP slots should exactly match the fleet
        """
        ships_found = 0
        for i, ship in enumerate(self.fleet):
            self.d(f"recherche du bateau #{i} (de taille {ship})")
            ship_found = False
            for (x, y) in doublerange(self.size):
                self.d(f"\tanalyse de la cellule {(x, y)}")
                if self @ (x, y) == WATER:
                    self.d(f"\tc'est de l'eau. cellule suivante...")
                    continue

                current_ship = ((x, y),)
                self.d(f"\tle bateau est maintenant {current_ship!r}")

                vertical_search_x = x
                self.d(f"\tVerticalement:")
                while len(current_ship) != ship:
                    vertical_search_x += 1
                    self.d(f"\t\tcellule ({vertical_search_x, y})")
                    if (
                        0 <= vertical_search_x <= self.size - 1
                        and self @ (vertical_search_x, y) == SHIP
                    ):
                        current_ship = (*current_ship, (vertical_search_x, y))
                        self.d(
                            f"\t\tajoutée au bateau, qui est maintenant {current_ship}"
                        )
                    else:
                        self.d(f"\t\tc'est de l'eau. Fin de la recherche verticale.")
                        break

                horizontal_search_y = y
                self.d(f"\tHorizontalement:")
                while len(current_ship) != ship:
                    horizontal_search_y += 1
                    self.d(f"\t\tcellule ({x, horizontal_search_y})")
                    if (
                        0 <= horizontal_search_y <= self.size - 1
                        and self @ (x, horizontal_search_y) == SHIP
                    ):
                        current_ship = (*current_ship, (x, horizontal_search_y))
                        self.d(
                            f"\t\t\tajoutée au bateau, qui est maintenant {current_ship}"
                        )
                    else:
                        self.d(f"\t\t\tc'est de leau.")
                        self.d(f"\t\tFin de la recherche horizontale.")
                        break

                if len(current_ship) == ship:
                    self.d(f"\t>> Le bateau a été trouvé!")
                    ship_found = True
                else:
                    self.d(f"\tLe bateau n'a pas été trouvé à partir de cette cellule.")
                    current_ship = ()

                if ship_found:
                    ships_found += 1
                    break
            if not ship_found:
                self.d(
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
        super().__init__(
            game, grid_size, initial_state=UNKNOWN, owner=owner or represents.owner
        )
        self.real_board = represents
        self.shots_missed = 0
        self.shots_fired = 0

    def handle_cell_Button1(self, x, y):
        if self.locked:
            self.d("board is locked! not firing.")
            return
        super().handle_cell_Button1(x, y)
        self.fire(x, y)

    def __xor__(self, coords):
        """aesthetics: ^ (x, y) to fire at (x, y)"""
        return self.fire(*coords)

    def fire(self, x: int, y: int) -> None:
        self.d(f"fire at x={x}, y={y}.")
        # # Don't fire if the cell is already known (i.e. has already been shot)
        # if (board @ (x, y)) != UNKNOWN:
        #     self.d(f"state={board @ (x, y)} is already known, not firing.")
        #     return

        hit_a_ship = self.real_board.fire(x, y)
        self.d(f"strategy is {self.owner.strategy}")
        self.owner.strategy.react_to_shot_result(x, y, hit_a_ship)
        self.d(f"fired, hit_a_ship={hit_a_ship}, changing cell state")

        self.change_cell(x, y, SUNKEN if hit_a_ship else MISSED)
        self.shots_fired += 1
        if not hit_a_ship:
            self.shots_missed += 1

        self.game.end_turn()
## Ai

class Strategy:
    name: str
    own_board: "ControlledBoard"
    ennemy_board: "ProjectiveBoard"

    def __init__(
        self, name: str, own_board: "ControlledBoard", ennemy_board: "ProjectiveBoard"
    ) -> None:
        self.name = name
        self.own_board = own_board
        self.ennemy_board = ennemy_board

    def choose_shot_location(self) :
        """
        Chooses where to fire the next shot
        """
        raise NotImplementedError("Please implement choose_shot_location.")

    def react_to_shot_result(self, x: int, y: int, hit_a_ship: bool) -> Any:
        """
        A hook that will be called once a shot is fired.
        Has access to whether the shot was successful (hit a ship) or not.
        """
        raise NotImplementedError("Please implement react_to_shot_result.")

    def d(self, t: str, *args, **kwargs):
        return self.own_board.d(
            f"[bold]{{Strategy [i]{self.name}[/i]}}[/bold] " + t, *args, **kwargs
        )


class HuntTarget(Strategy):
    name: str = "Hunt & Target"

    def __init__(
        self, name: str, own_board: "ControlledBoard", ennemy_board: "ProjectiveBoard"
    ) -> None:
        super().__init__(name, own_board, ennemy_board)
        self.potential_targets = []
        self.already_hit = []
        self.name = "Hunt & Target"

    def choose_shot_location(self) :
        if self.potential_targets == []:
            return self.ennemy_board.random_coordinates()
        else:
            return self.potential_targets.pop()

    def react_to_shot_result(self, x: int, y: int, hit_a_ship: bool) -> Any:
        self.already_hit.append((x, y))

        if hit_a_ship:
            self.potential_targets += [
                target for target in
                self.ennemy_board.cardinal_coordinates(x, y)
                if self.ennemy_board.within_bounds(*target)
                and target not in self.already_hit
            ]
            self.d(f"potential targets are {self.potential_targets}")


class NoStrategy(Strategy):

    name = "None"

    def __init__(
        self,
        name: str = "None",
        own_board: "ControlledBoard" = None,
        ennemy_board: "ProjectiveBoard" = None,
    ):
        return

    def choose_shot_location(self) :
        return (0, 0)

    def react_to_shot_result(self, x: int, y: int, hit_a_ship: bool) -> Any:
        return

    def d(self, t: str, *args, **kwargs):
        return
## Player

# Constantes
PLACING = 4
SHOOTING = 5
DECIDING = 6

FLEET = [DESTROYER, CRUISER, SUBMARINE, BATTLESHIP, AIRCRAFT_CARRIER]
HELPTEXT_PLACING = (
    f"Placez vos bateaux (de longueurs {french_join(FLEET)}),\npuis cliquez sur OK.\nE = Eau, B = Bateau, T = Touché, M = Manqué.\n"
)
HELPTEXT_WRONG = f"Veuillez placer tout les bateaux correctement\n\n{HELPTEXT_PLACING}"
HELPTEXT_SHOOTING = "Cliquez sur une case '?' pour tirer à cet endroit."


class Player:
    own_board: ControlledBoard
    ennemy_board: ProjectiveBoard
    ok_button: Button
    game: "Game"
    index: int
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
            self.ennemy_board.real_board @ (x, y) != SHIP
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
        self.own_board.render(0, 2)
        self.ennemy_board.render(0, 1)
        self.ok_button.grid(column=1, row=2)

    def handle_click_ok(self, event) -> Any:
        if self.game.phase == PLACING:
            self.d(
                f"handling OK button click: locking board, switching to shooting phase"
            )
            if not self.own_board.legal:
                self.d(f"board is not legal! not locking & switching phase.")
                self.game.helptext_var.set(HELPTEXT_WRONG)
                return
            self.own_board.lock()
            self.game.phase = SHOOTING
            self.game.helptext_var.set(HELPTEXT_SHOOTING)

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

    def decide_coordinates(self) :
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

    def place_ship(self, coords) -> None:
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
        if orientation == VERTICAL:
            return [
                self.own_board @ (x, y)
                for (x, y) in self.own_board.vertical_coordinates(y, x, x + ship)
            ] == [WATER] * ship
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
## Main

FLEET = [DESTROYER, CRUISER, SUBMARINE, BATTLESHIP, AIRCRAFT_CARRIER]
GRID_SIZE = 10


class DummyPlayer:
    def __init__(self, name: str, human: bool) -> None:
        self.name = name
        self.human = human


class Game:
    phase: int
    current_player_index: int
    helptext_var: StringVar

    def __init__(self) -> None:
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.phase = PLACING
        self.current_player_index = 0
        self.helptext_var = StringVar()

        user_board = ControlledBoard(
            self, grid_size=GRID_SIZE, fleet=FLEET, owner=DummyPlayer("Chirex", True)
        )
        bot_board = ControlledBoard(
            self,
            grid_size=GRID_SIZE,
            fleet=FLEET,
            owner=DummyPlayer("Léonard de Vinci", False),
        )

        self.user = HumanPlayer(
            self,
            user_board,
            ennemy_board=bot_board,
            index=0,
            name=input("Choisissez votre nom: "),
        )
        self.bot = AIPlayer(
            self,
            bot_board,
            ennemy_board=user_board,
            index=1,
            name="Léonard De Vinci",
            strategy=HuntTarget,
        )
        self.players = [self.user, self.bot]

        self.bot.place_ships()
        d("ennemy state is", end=" ")
        pprint(self.bot.own_board.state)

    def start(self):
        self.helptext_var.set(HELPTEXT_PLACING)
        Label(self.root, textvariable=self.helptext_var).grid(column=0, row=0)

        Label(self.root, text=self.bot.name).grid(column=0, row=1)
        self.user.ennemy_board.render(0, 2)
        Label(self.root, text=self.user.name).grid(column=0, row=3)
        self.user.own_board.render(0, 4)

        self.user.ok_button.grid(column=0, row=5)
        self.root.mainloop()

    @property
    def winner(self) -> Optional[Player]:
        for _, player in enumerate(self.players):
            if player.won:
                return player
        return None

    def end_turn(self):
        if self.winner is not None:
            self.helptext_var.set(
                f"Bravo, {self.winner.name}! Vous avez gagné avec une précsion de {(self.winner.accuracy or 0)*100}%"
            )
            self.winner.ennemy_board.lock()
        else:
            self.current_player_index = (self.current_player_index + 1) % 2
            if self.bot.turn_is_mine():
                self.bot.ennemy_board.fire(*self.bot.decide_coordinates())

    @property
    def current_player(self) -> Player:
        return [self.user, self.bot][self.current_player_index]


if __name__ == "__main__":
    print(f"fleet is {FLEET}")
    Game().start()
