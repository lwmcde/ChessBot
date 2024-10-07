from chess.chess_board import ChessBoard

class ChessGameManager:
    def __init__(self):
        self.games = []

    def start_new_game(self):
        game = ChessBoard()
        self.games.append(game)
        return game

    def load_game(self, initial_state):
        game = ChessBoard(initial_state)
        self.games.append(game)
        return game

    def get_all_games(self):
        return self.games

# Example usage
if __name__ == "__main__":
    manager = ChessGameManager()
    game1 = manager.start_new_game()
    game2 = manager.load_game([[None]*8 for _ in range(8)])  # Example of loading an empty board
    game1.print_board()
    print("\n")
    game2.print_board()