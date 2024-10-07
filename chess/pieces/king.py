from .base_piece import ChessPiece

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