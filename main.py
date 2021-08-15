from ai import HuntTarget
from tkinter import StringVar, Tk, Label
from typing import Optional
from utils import *
from board import (
    ControlledBoard,
    DESTROYER,
    CRUISER,
    SUBMARINE,
    BATTLESHIP,
    AIRCRAFT_CARRIER,
)
from player import Player, HumanPlayer, AIPlayer, PLACING, HELPTEXT_PLACING
from rich import print as pprint

FLEET = [DESTROYER, CRUISER, SUBMARINE, BATTLESHIP, AIRCRAFT_CARRIER]
GRID_SIZE = 10


class DummyPlayer:
    def __init__(self, name: str, human: bool) -> None:
        self.name = name
        self.human = human


class Game:
    phase: int
    current_player_index: int
    players: list[Player]
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
            self, user_board, ennemy_board=bot_board, index=0, name="Chirex"
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
        Label(
            self.root,
            textvariable=self.helptext_var
        ).grid(column=0, row=0)

        self.user.render()
        # self.bot.ennemy_board.render(2, 0)
        # self.bot.own_board.render(2, 1)
        self.root.mainloop()

    @property
    def winner(self) -> Optional[Player]:
        for _, player in enumerate(self.players):
            if player.won:
                return player
        return None

    def end_turn(self):
        if self.winner is not None:
            self.helptext_var.set(f"Bravo, {self.winner.name}! Vous avez gagné avec une précsion de {(self.winner.accuracy or 0)*100}%")
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
