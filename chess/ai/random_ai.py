import random
from chess.pieces import Queen, Rook, Bishop, Knight, Pawn
from chess.ai.base_ai import BaseAI

class RandomAI(BaseAI):
    def __init__(self, color):
        self.color = color

    def make_move(self, chess_board, player_flipped):
        all_moves = []
        ai_flipped = player_flipped
        for row in range(8):
            for col in range(8):
                piece = chess_board.board[row][col]
                if piece and piece.color == self.color:
                    valid_moves = chess_board.get_valid_moves((row, col), flipped=ai_flipped)
                    for move in valid_moves:
                        # Simulate the move
                        original_piece = chess_board.board[move[0]][move[1]]
                        chess_board.board[move[0]][move[1]] = piece
                        chess_board.board[row][col] = None
                        in_check = chess_board.is_in_check(self.color)
                        # Undo the move
                        chess_board.board[row][col] = piece
                        chess_board.board[move[0]][move[1]] = original_piece
                        if not in_check:
                            all_moves.append(((row, col), move))

        if all_moves:
            chosen_move = random.choice(all_moves)
            # chess_board.update_board(chosen_move)  # Ensure this line is present to apply the move
            start, end = chosen_move
            piece = chess_board.board[start[0]][start[1]]

            # Handle promotion
            if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
                promotion_choice = self.choose_promotion_piece()
                return chosen_move, promotion_choice  # Return the move and promotion choice

            return chosen_move, None  # Return the move without promotion
        return None, None

    def choose_promotion_piece(self):
        return random.choice([Queen, Rook, Bishop, Knight])