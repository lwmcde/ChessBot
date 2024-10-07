from .base_piece import ChessPiece

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