import copy
import concurrent.futures
from chess.ai.base_ai import BaseAI
from chess.ai.evaluation import basic_material_evaluation, advanced_evaluation
from chess.pieces import Queen, Rook, Bishop, Knight, Pawn

class MinimaxAI(BaseAI):
    def __init__(self, color):
        super().__init__(color, advanced_evaluation)
        self.transposition_table = {}

    def make_move(self, chess_board, player_flipped):
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # Iterative deepening
        for depth in range(1, 3):  # Adjust the range for desired depth
            best_move = None
            best_value = float('-inf')

            # Use a ThreadPoolExecutor for parallel move evaluation
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for move in self.get_all_possible_moves(chess_board, self.color):
                    futures.append(executor.submit(self.evaluate_move, chess_board, move, alpha, beta, depth))

                for future in concurrent.futures.as_completed(futures):
                    move_value, move = future.result()
                    if move_value > best_value:
                        best_value = move_value
                        best_move = move

        # Apply the best move to the actual board
        if best_move:
            start, end = best_move
            piece = chess_board.board[start[0]][start[1]]

            if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
                chess_board.board[end[0]][end[1]] = Queen(self.color)
                chess_board.board[start[0]][start[1]] = None
            #else:
             
             #   chess_board.update_board(best_move)

        return best_move, None

    def evaluate_move(self, chess_board, move, alpha, beta, depth):
        start, end = move
        piece = chess_board.board[start[0]][start[1]]

        board_copy = copy.deepcopy(chess_board)
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            board_copy.board[end[0]][end[1]] = Queen(self.color)
            board_copy.board[start[0]][start[1]] = None
        else:
            board_copy.update_board(move)

        move_value = self.minimax(board_copy, depth, False, alpha, beta)
        return move_value, move

    def minimax(self, chess_board, depth, maximizing_player, alpha, beta):
        if depth == 0 or chess_board.is_checkmate(self.color) or chess_board.is_stalemate(self.color):
            return self.evaluate_board(chess_board)

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(chess_board, self.color):
                chess_board.update_board(move)
                eval = self.minimax(chess_board, depth - 1, False, alpha, beta)
                chess_board.undo_move()
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
                chess_board.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_ordered_moves(self, chess_board, color):
        moves = self.get_all_possible_moves(chess_board, color)
        # Simple move ordering: prioritize captures and checks
        def move_priority(move):
            start, end = move
            piece = chess_board.board[start[0]][start[1]]
            target = chess_board.board[end[0]][end[1]]
            # Higher priority for captures and checks
            return (target is not None, isinstance(piece, (Queen, Rook, Bishop, Knight)))

        return sorted(moves, key=move_priority, reverse=True)

    def hash_board(self, chess_board):
        # Simple hash function for the board state
        return hash(str(chess_board.board))