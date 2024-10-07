from .base_piece import ChessPiece

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