from .base_piece import ChessPiece

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