from .base_piece import ChessPiece
from .rook import Rook
from .bishop import Bishop

class Queen(ChessPiece):
    symbol = 'Q'

    def valid_moves(self, position, board, flipped=False, last_move=None):
        # Queen combines the moves of Rook and Bishop
        return Rook(self.color).valid_moves(position, board) + Bishop(self.color).valid_moves(position, board)