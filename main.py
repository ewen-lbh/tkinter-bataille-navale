from tkinter import Tk, Label
from typing import Optional
from utils import *
from board import ControlledBoard
from player import Player, HumanPlayer, AIPlayer

# Constantes
PLACING = 4
SHOOTING = 5
DECIDING = 6


class Game:
    phase: int
    current_player_index: int
    players: list[Player]

    def __init__(self) -> None:
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.phase = PLACING
        self.current_player_index = 0

        user_board = ControlledBoard(self, grid_size=10, ships=5 + 4 + 3 + 2 + 1)
        bot_board = ControlledBoard(self, grid_size=10, ships=5 + 4 + 3 + 2 + 1)

        self.user = HumanPlayer(
            self, user_board, ennemy_board=bot_board, index=0, name="Chirex"
        )
        self.bot = AIPlayer(
            self, bot_board, ennemy_board=user_board, index=1, name="Léonard De Vinci"
        )
        self.players = [self.user, self.bot]

        self.bot.place_ships()

    def start(self):
        self.user.render()
        # self.bot.ennemy_board.render(2, 0)
        # self.bot.own_board.render(2, 1)
        self.root.mainloop()

    def winner(self) -> Optional[Player]:
        for _, player in enumerate(self.players):
            if player.won:
                return player
        return None

    def end_turn(self):
        if (winner := self.winner()) is not None:
            for player in self.players:
                player.own_board.mainframe.grid(column=0, row=2)
            Label(self.root, text=f"Congratulations, {winner.name}. You won!").grid(
                column=0, row=1
            )
        else:
            self.current_player_index = (self.current_player_index + 1) % 2
            if self.bot.is_it_my_turn():
                self.bot.ennemy_board.fire(
                    *self.bot.ennemy_board.real_board.random_coordinates()
                )

    @property
    def current_player(self) -> Player:
        return [self.user, self.bot][self.current_player_index]


if __name__ == "__main__":
    Game().start()
