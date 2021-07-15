from typing import Any
from utils import *
from rich import print as pprint


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

    def choose_shot_location(self) -> tuple[int, int]:
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


HUNT = 100
TARGET = 200


class HuntTarget(Strategy):

    potential_targets: list[tuple[int, int]] = attr.field(factory=list)
    current_mode: int = HUNT
    name: str = "Hunt & Target"

    def __init__(
        self, name: str, own_board: "ControlledBoard", ennemy_board: "ProjectiveBoard"
    ) -> None:
        super().__init__(name, own_board, ennemy_board)
        self.potential_targets = []
        self.current_mode = HUNT
        self.name = "Hunt & Target"

    def choose_shot_location(self) -> tuple[int, int]:
        self.d(f"current mode is {self.current_mode}")
        if self.current_mode == HUNT:
            return self.ennemy_board.random_coordinates()
        else:
            return self.potential_targets.pop()

    def react_to_shot_result(self, x: int, y: int, hit_a_ship: bool) -> Any:
        if hit_a_ship:
            self.current_mode = TARGET
        elif self.potential_targets == []:
            self.current_mode = HUNT

        self.d(f"switched current mode to {self.current_mode}.")

        if self.current_mode == TARGET:
            self.d(
                f"adding potential targets {self.ennemy_board.cardinal_coordinates(x, y)}",
                end="",
            )
            self.potential_targets = (
                list(self.ennemy_board.cardinal_coordinates(x, y))
                + self.potential_targets
            )
            pprint(self.potential_targets)


class NoStrategy(Strategy):

    name = "None"

    def __init__(
        self,
        name: str = "None",
        own_board: "ControlledBoard" = None,
        ennemy_board: "ProjectiveBoard" = None,
    ):
        return

    def choose_shot_location(self) -> tuple[int, int]:
        return (0, 0)

    def react_to_shot_result(self, x: int, y: int, hit_a_ship: bool) -> Any:
        return

    def d(self, t: str, *args, **kwargs):
        return
