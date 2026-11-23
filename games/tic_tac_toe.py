"""Two players share a terminal. Use T, M or B and a column from 1 to 3."""

ROWS = tuple(tuple(f"{row}{col}" for col in range(1, 4)) for row in "TMB")
LINES = (*ROWS, *zip(*ROWS), ("T1", "M2", "B3"), ("T3", "M2", "B1"))


def play():
    board = {cell: cell for row in ROWS for cell in row}
    for turn in range(9):
        print("\n".join(" | ".join(board[c] for c in row) for row in ROWS))
        player = "XO"[turn % 2]
        while True:
            try:
                cell = input(f"{player}, choose a square: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\nGame closed.")
                return
            if cell in board and board[cell] == cell:
                break
            print("Choose an unoccupied square, for example M2.")
        board[cell] = player
        if any(all(board[c] == player for c in line) for line in LINES):
            print(f"{player} wins!")
            return
    print("Draw.")


if __name__ == "__main__":
    play()
