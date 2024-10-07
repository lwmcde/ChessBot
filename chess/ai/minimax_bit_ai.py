from chess.bitboard import BitboardChessBoard
from chess.chess_board import ChessBoard
from chess.ai.base_ai import BaseAI
from chess.ai.evaluation import basic_material_evaluation
import copy

class MinimaxBitAI(BaseAI):
    def __init__(self, color, depth=3):
        super().__init__(color, basic_material_evaluation)
        self.depth = depth

    def make_move(self, chess_board, player_flipped):
        # Convert the traditional board to a bitboard
        bitboard = chess_board.board_to_bitboard()

        # Perform minimax to find the best move
        best_move, _ = self.minimax(bitboard, self.depth, True, float('-inf'), float('inf'))

        # Debug: Check if a move was found
        if best_move is None:
            print("No valid moves found by MinimaxBitAI")
            raise Exception("No valid moves found by MinimaxBitAI")

        # Apply the best move to the traditional board
        start, end = best_move
        chess_board.update_board((start, end))
        return best_move, None

    def minimax(self, bitboard, depth, maximizing_player, alpha, beta):
        if depth == 0 or self.is_terminal_node(bitboard):
            return None, self.evaluate_board(bitboard)

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in bitboard.generate_moves(self.color):
                bitboard.update_board(*move)
                _, eval = self.minimax(bitboard, depth - 1, False, alpha, beta)
                bitboard.undo_move()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            min_eval = float('inf')
            opponent_color = 'black' if self.color == 'white' else 'white'
            for move in bitboard.generate_moves(opponent_color):
                bitboard.update_board(*move)
                _, eval = self.minimax(bitboard, depth - 1, True, alpha, beta)
                bitboard.undo_move()
                if eval < min_eval:
                    min_eval = eval
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return None, min_eval

    def evaluate_board(self, bitboard):
        # Implement a simple evaluation function
        piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
                        'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': 0}
        score = 0
        for piece, bitboard_value in bitboard.bitboards.items():
            score += piece_values[piece] * bin(bitboard_value).count('1')
        return score

    def is_terminal_node(self, bitboard):
        # Check for checkmate or stalemate
        return bitboard.is_checkmate(self.color) or bitboard.is_stalemate(self.color)