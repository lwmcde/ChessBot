from chess.pieces import Queen

from abc import ABC, abstractmethod

class BaseAI(ABC):
    def __init__(self, color, evaluation_function):
        self.color = color
        self.evaluation_function = evaluation_function
        self.evaluation_cache = {}

    @abstractmethod
    def make_move(self, chess_board, player_flipped):
        pass

    def minimax(self, chess_board, depth, maximizing_player, alpha, beta):
        if depth == 0 or chess_board.is_checkmate(self.color) or chess_board.is_stalemate(self.color):
            return self.evaluate_board(chess_board)

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(chess_board, self.color):
                chess_board.update_board(move)
                eval = self.minimax(chess_board, depth - 1, False, alpha, beta)
                chess_board.undo_move(move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            opponent_color = 'black' if self.color == 'white' else 'white'
            for move in self.get_all_possible_moves(chess_board, opponent_color):
                chess_board.update_board(move)
                eval = self.minimax(chess_board, depth - 1, True, alpha, beta)
                chess_board.undo_move(move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_board(self, chess_board):
        # Check if the board state is cached
        board_state = tuple(tuple(row) for row in chess_board.board)
        if board_state in self.evaluation_cache:
            return self.evaluation_cache[board_state]

        # Use the provided evaluation function
        value = self.evaluation_function(chess_board, self.color)

        # Cache the evaluation
        self.evaluation_cache[board_state] = value
        return value

    def get_all_possible_moves(self, chess_board, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = chess_board.board[row][col]
                if piece and piece.color == color:
                    valid_moves = chess_board.get_valid_moves((row, col))
                    for move in valid_moves:
                        # Simulate the move
                        original_piece = chess_board.board[move[0]][move[1]]
                        chess_board.board[move[0]][move[1]] = piece
                        chess_board.board[row][col] = None
                        in_check = chess_board.is_in_check(color)
                        # Undo the move
                        chess_board.board[row][col] = piece
                        chess_board.board[move[0]][move[1]] = original_piece
                        if not in_check:
                            moves.append(((row, col), move))
        return moves