class ChessPiece:
    def __init__(self, color):
        self.color = color

    def valid_moves(self, position, board):
        raise NotImplementedError("This method should be overridden by subclasses")

    def __str__(self):
        return self.symbol