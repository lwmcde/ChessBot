from .pieces import Pawn, Rook, Knight, Bishop, Queen, King
from .bitboard import BitboardChessBoard, create_piece_from_symbol

class ChessBoard:
    def __init__(self, initial_state=None, flipped=False):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None
        self.move_history = []  # Initialize move history
        self.king_moved = {'white': False, 'black': False}
        self.rook_moved = {'white': [False, False], 'black': [False, False]}  # [left rook, right rook]
        if initial_state:
            self.load_state(initial_state)
        else:
            self.setup_initial_position(flipped)

    def setup_initial_position(self, flipped):
        if not flipped:
            # White pieces at the bottom
            self.board[0] = [
                Rook('black'), Knight('black'), Bishop('black'), Queen('black'),
                King('black'), Bishop('black'), Knight('black'), Rook('black')
            ]
            self.board[1] = [Pawn('black') for _ in range(8)]
            self.board[6] = [Pawn('white') for _ in range(8)]
            self.board[7] = [
                Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
                King('white'), Bishop('white'), Knight('white'), Rook('white')
            ]
        else:
            # Black pieces at the bottom
            self.board[0] = [
                Rook('white'), Knight('white'), Bishop('white'), King('white'),
                Queen('white'), Bishop('white'), Knight('white'), Rook('white')
            ]
            self.board[1] = [Pawn('white') for _ in range(8)]
            self.board[6] = [Pawn('black') for _ in range(8)]
            self.board[7] = [
                Rook('black'), Knight('black'), Bishop('black'), King('black'),
                Queen('black'), Bishop('black'), Knight('black'), Rook('black')
            ]

    def load_state(self, state):
        self.board = state

    def update_board(self, move):
        start, end = move
        piece = self.board[start[0]][start[1]]
        captured_piece = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None

        # Save the move to history for undoing
        self.move_history.append((start, end, captured_piece))

        # Handle castling
        if isinstance(piece, King) and abs(start[1] - end[1]) == 2:
            if end[1] > start[1]:  # Kingside castling
                self.board[end[0]][end[1] - 1] = self.board[end[0]][7]  # Move rook to the king's left
                self.board[end[0]][7] = None
            else:  # Queenside castling
                self.board[end[0]][end[1] + 1] = self.board[end[0]][0]  # Move rook to the king's right
                self.board[end[0]][0] = None

        # Update move tracking
        if isinstance(piece, King):
            self.king_moved[piece.color] = True
        elif isinstance(piece, Rook) and not self.king_moved[piece.color]:
            king_col = None
            for col in range(8):
                if isinstance(self.board[start[0]][col], King) and self.board[start[0]][col].color == piece.color:
                    king_col = col
                    break

            if king_col is not None and not self.king_moved[piece.color]:
                if abs(start[1] - king_col) < abs(7 - king_col):
                    self.rook_moved[piece.color][0] = True  # Queenside rook
                else:
                    self.rook_moved[piece.color][1] = True  # Kingside rook

        # Handle en passant capture
        if isinstance(piece, Pawn) and abs(start[1] - end[1]) == 1 and self.board[end[0]][end[1]] is None:
            self.board[start[0]][end[1]] = None

        self.last_move = move

    def undo_move(self):
        if not self.move_history:
            return

        start, end, captured_piece = self.move_history.pop()
        piece = self.board[end[0]][end[1]]
        self.board[start[0]][start[1]] = piece
        self.board[end[0]][end[1]] = captured_piece

        # Handle castling undo
        if isinstance(piece, King) and abs(start[1] - end[1]) == 2:
            if end[1] > start[1]:  # Kingside castling
                self.board[end[0]][7] = self.board[end[0]][end[1] - 1]
                self.board[end[0]][end[1] - 1] = None
            else:  # Queenside castling
                self.board[end[0]][0] = self.board[end[0]][end[1] + 1]
                self.board[end[0]][end[1] + 1] = None

        # Update move tracking
        if isinstance(piece, King):
            self.king_moved[piece.color] = False
        elif isinstance(piece, Rook):
            # Reset rook moved status if necessary
            pass  # Implement logic if needed

        # Handle en passant undo
        if isinstance(piece, Pawn) and abs(start[1] - end[1]) == 1 and captured_piece is None:
            self.board[start[0]][end[1]] = Pawn(piece.color)

        self.last_move = None if not self.move_history else self.move_history[-1]

    def get_valid_moves(self, position, flipped=False):
        x, y = position
        piece = self.board[x][y]
        if piece:
            moves = piece.valid_moves(position, board=self.board, flipped=flipped, last_move=self.last_move)
            if isinstance(piece, King):
                moves.extend(self.get_castling_moves(piece.color, x))
            return moves
        return []

    def print_board_state(self):
        for row in self.board:
            print(' '.join([piece.symbol if piece else '.' for piece in row]))
        print("\n")

    def get_castling_moves(self, color, row):
        castling_moves = []
        king_col = None

        # Find the current position of the king
        for col in range(8):
            if isinstance(self.board[row][col], King) and self.board[row][col].color == color:
                king_col = col
                break

        if king_col is None:
            return castling_moves  # No king found, return empty list

        if not self.king_moved[color]:
            # Determine the rook positions and directions based on the king's column
            kingside_rook_col = 7 if king_col < 4 else 0
            queenside_rook_col = 0 if king_col < 4 else 7
            kingside_direction = 1 if not king_col < 4 else -1
            queenside_direction = -1 if not king_col < 4 else 1

            # Kingside castling
            if not self.rook_moved[color][1] and self.board[row][kingside_rook_col] is not None:
                if isinstance(self.board[row][kingside_rook_col], Rook) and self.board[row][kingside_rook_col].color == color:
                    if all(0 <= king_col + i * kingside_direction < 8 and self.board[row][king_col + i * kingside_direction] is None for i in range(1, 3)):
                        if not self.is_in_check(color) and not self.is_square_attacked((row, king_col + kingside_direction), color) and not self.is_square_attacked((row, king_col + 2 * kingside_direction), color):
                            castling_moves.append((row, king_col + 2 * kingside_direction))

            # Queenside castling
            if not self.rook_moved[color][0] and self.board[row][queenside_rook_col] is not None:
                if isinstance(self.board[row][queenside_rook_col], Rook) and self.board[row][queenside_rook_col].color == color:
                    if all(0 <= king_col + i * queenside_direction < 8 and self.board[row][king_col + i * queenside_direction] is None for i in range(1, 4)):
                        if not self.is_in_check(color) and not self.is_square_attacked((row, king_col + queenside_direction), color) and not self.is_square_attacked((row, king_col + 2 * queenside_direction), color):
                            castling_moves.append((row, king_col + 2 * queenside_direction))

        return castling_moves

    def is_square_attacked(self, position, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if position in piece.valid_moves((row, col), self.board):
                        return True
        return False

    def is_in_check(self, color):
        king_position = self.find_king(color)
        if not king_position:
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if king_position in piece.valid_moves((row, col), self.board):
                        return True
        return False

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.valid_moves((row, col), self.board):
                        # Simulate the move
                        original_piece = self.board[move[0]][move[1]]
                        self.board[move[0]][move[1]] = piece
                        self.board[row][col] = None
                        in_check = self.is_in_check(color)
                        # Undo the move
                        self.board[row][col] = piece
                        self.board[move[0]][move[1]] = original_piece
                        if not in_check:
                            return False
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    valid_moves = self.get_valid_moves((row, col))
                    if valid_moves:
                        return False

        return True

    def board_to_bitboard(chess_board):
        bitboard = BitboardChessBoard()
        for row in range(8):
            for col in range(8):
                piece = chess_board.board[row][col]
                if piece:
                    position = row * 8 + col
                    symbol = piece.symbol.lower() if piece.color == 'black' else piece.symbol.upper()
                    bitboard.set_piece(symbol, position)
        return bitboard

    def bitboard_to_board(bitboard, chess_board):
        for piece, bb in bitboard.bitboards.items():
            while bb:
                position = bb.bit_length() - 1
                row, col = divmod(position, 8)
                # Create a new piece instance based on the symbol
                piece_instance = create_piece_from_symbol(piece)
                chess_board.board[row][col] = piece_instance
                bb &= ~(1 << position)