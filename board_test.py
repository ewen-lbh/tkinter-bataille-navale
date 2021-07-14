from board import AIRCRAFT_CARRIER, ControlledBoard, DESTROYER, SUBMARINE, BATTLESHIP
from main import Game


def test_ControlledBoard_legal():
    board = ControlledBoard(
        Game(), grid_size=6, fleet={BATTLESHIP, DESTROYER, SUBMARINE}
    )
    board.state = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0],
    ]

    assert board.legal

    board.state = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
    ]

    assert board.legal

    board.state = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 1, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0],
    ]

    assert not board.legal


if __name__ == "__main__":
    [testfunc() for name, testfunc in locals().items() if name.startswith("test_")]
