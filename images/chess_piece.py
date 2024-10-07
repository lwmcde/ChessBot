class ChessPiece:
    def __init__(self, color):
        self.color = color

    def valid_moves(self, position, board):
        raise NotImplementedError("This method should be overridden by subclasses")

    def __str__(self):
        return self.symbol

class Pawn(ChessPiece):
    symbol = 'P'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        x, y = position
        moves = []

        # Determine direction based on color and flipped state
        if self.color == 'white':
            direction = 1 if flipped else -1
            start_row = 6 if not flipped else 1
        else:
            direction = -1 if flipped else 1
            start_row = 1 if not flipped else 6

        # Move forward
        if 0 <= x + direction < 8 and board[x + direction][y] is None:
            moves.append((x + direction, y))
            # Double move from starting position
            if x == start_row and board[x + 2 * direction][y] is None:
                moves.append((x + 2 * direction, y))

        # Capture diagonally
        for dy in [-1, 1]:
            if 0 <= y + dy < 8 and 0 <= x + direction < 8:
                if board[x + direction][y + dy] is not None and board[x + direction][y + dy].color != self.color:
                    moves.append((x + direction, y + dy))


        # En passant
        if last_move:
            (last_start, last_end) = last_move
            if abs(last_start[0] - last_end[0]) == 2 and last_start[1] == last_end[1]:
                if last_end[0] == x and abs(last_end[1] - y) == 1:
                    if board[last_end[0]][last_end[1]].symbol == 'P' and board[last_end[0]][last_end[1]].color != self.color:
                        moves.append((x + direction, last_end[1]))



        return moves

class Rook(ChessPiece):
    symbol = 'R'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        x, y = position
        moves = []

        # Horizontal and vertical moves
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x, y
            while True:
                nx += dx
                ny += dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    if board[nx][ny] is None:
                        moves.append((nx, ny))
                    elif board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                        break
                    else:
                        break
                else:
                    break

        return moves

class Knight(ChessPiece):
    symbol = 'N'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        x, y = position
        moves = []

        # L-shaped moves
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] is None or board[nx][ny].color != self.color:
                    moves.append((nx, ny))

        return moves

class Bishop(ChessPiece):
    symbol = 'B'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        x, y = position
        moves = []

        # Diagonal moves
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x, y
            while True:
                nx += dx
                ny += dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    if board[nx][ny] is None:
                        moves.append((nx, ny))
                    elif board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                        break
                    else:
                        break
                else:
                    break

        return moves

class Queen(ChessPiece):
    symbol = 'Q'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        # Queen combines the moves of Rook and Bishop
        return Rook(self.color).valid_moves(position, board) + Bishop(self.color).valid_moves(position, board)

class King(ChessPiece):
    symbol = 'K'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        x, y = position
        moves = []

        # One square in any direction
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] is None or board[nx][ny].color != self.color:
                    moves.append((nx, ny))

        return moves