from .pieces import Pawn, Rook, Knight, Bishop, Queen, King

class BitboardChessBoard:
    def __init__(self, flipped=False):
        # Initialize bitboards for each piece type and color
        self.bitboards = {
            'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,  # White pieces
            'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0   # Black pieces
        }
        self.occupied = 0  # All occupied squares
        self.king_moved = {'white': False, 'black': False}
        self.rook_moved = {'white': [False, False], 'black': [False, False]}
        self.last_move = None
        self.move_history = []
        self.setup_initial_position(flipped)

        # Precomputed move bitboards for knights and kings
        self.knight_moves = self.precompute_knight_moves()
        self.king_moves = self.precompute_king_moves()

    def precompute_knight_moves(self):
        knight_moves = [0] * 64
        for position in range(64):
            moves = 0
            row, col = divmod(position, 8)
            knight_offsets = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]
            for dr, dc in knight_offsets:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves |= (1 << (new_row * 8 + new_col))
            knight_moves[position] = moves
        return knight_moves

    def precompute_king_moves(self):
        king_moves = [0] * 64
        for position in range(64):
            moves = 0
            row, col = divmod(position, 8)
            king_offsets = [
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
            for dr, dc in king_offsets:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves |= (1 << (new_row * 8 + new_col))
            king_moves[position] = moves
        return king_moves

    def setup_initial_position(self, flipped):
        if not flipped:
            # White pieces at the bottom
            self.set_piece('R', 0)
            self.set_piece('N', 1)
            self.set_piece('B', 2)
            self.set_piece('Q', 3)
            self.set_piece('K', 4)
            self.set_piece('B', 5)
            self.set_piece('N', 6)
            self.set_piece('R', 7)
            for i in range(8, 16):
                self.set_piece('P', i)
            for i in range(48, 56):
                self.set_piece('p', i)
            self.set_piece('r', 56)
            self.set_piece('n', 57)
            self.set_piece('b', 58)
            self.set_piece('q', 59)
            self.set_piece('k', 60)
            self.set_piece('b', 61)
            self.set_piece('n', 62)
            self.set_piece('r', 63)
        else:
            # Black pieces at the bottom
            self.set_piece('r', 0)
            self.set_piece('n', 1)
            self.set_piece('b', 2)
            self.set_piece('q', 3)
            self.set_piece('k', 4)
            self.set_piece('b', 5)
            self.set_piece('n', 6)
            self.set_piece('r', 7)
            for i in range(8, 16):
                self.set_piece('p', i)
            for i in range(48, 56):
                self.set_piece('P', i)
            self.set_piece('R', 56)
            self.set_piece('N', 57)
            self.set_piece('B', 58)
            self.set_piece('Q', 59)
            self.set_piece('K', 60)
            self.set_piece('B', 61)
            self.set_piece('N', 62)
            self.set_piece('R', 63)

    def set_piece(self, piece, position):
        self.bitboards[piece] |= (1 << position)
        self.occupied |= (1 << position)

    def clear_piece(self, piece, position):
        self.bitboards[piece] &= ~(1 << position)
        self.occupied &= ~(1 << position)

    def move_piece(self, piece, start, end):
        self.clear_piece(piece, start)
        self.set_piece(piece, end)

    def get_piece_at(self, position):
        for piece, bitboard in self.bitboards.items():
            if bitboard & (1 << position):
                return piece
        return None

    def update_board(self, start, end):
        piece = self.get_piece_at(start)
        if piece:
            self.move_piece(piece, start, end)
            self.last_move = (start, end)
            self.move_history.append((start, end, piece))

    def undo_move(self):
        if not self.move_history:
            return

        start, end, piece = self.move_history.pop()
        self.move_piece(piece, end, start)
        self.clear_piece(piece, end)
        self.last_move = None if not self.move_history else self.move_history[-1]

    def is_square_attacked(self, position, color):
        opponent_pieces = ['p', 'n', 'b', 'r', 'q', 'k'] if color == 'white' else ['P', 'N', 'B', 'R', 'Q', 'K']
        
        # Check for knight attacks
        knight_moves = self.knight_moves[position]
        if knight_moves & self.bitboards[opponent_pieces[1]]:  # Check against opponent knights
            return True

        # Check for king attacks
        king_moves = self.king_moves[position]
        if king_moves & self.bitboards[opponent_pieces[5]]:  # Check against opponent king
            return True

        # Check for pawn attacks
        pawn_attack_offsets = [-9, -7] if color == 'white' else [7, 9]
        for offset in pawn_attack_offsets:
            attack_pos = position + offset
            if 0 <= attack_pos < 64 and self.bitboards[opponent_pieces[0]] & (1 << attack_pos):
                return True

        # Check for sliding piece attacks (bishops, rooks, queens)
        for direction in [9, 7, -9, -7, 8, -8, 1, -1]:
            current_pos = position
            while True:
                current_pos += direction
                if not (0 <= current_pos < 64) or (current_pos % 8 == 0 and direction in [7, -9, -1]) or (current_pos % 8 == 7 and direction in [9, -7, 1]):
                    break
                if self.occupied & (1 << current_pos):
                    piece = self.get_piece_at(current_pos)
                    if piece in opponent_pieces[2:5]:  # Check against bishops, rooks, queens
                        return True
                    break

        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        for move in self.generate_moves(color):
            self.update_board(*move)
            if not self.is_in_check(color):
                self.undo_move()
                return False
            self.undo_move()
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        for move in self.generate_moves(color):
            self.update_board(*move)
            if not self.is_in_check(color):
                self.undo_move()
                return False
            self.undo_move()
        return True

    def is_in_check(self, color):
        king_position = self.find_king(color)
        if king_position is None:
            return False
        return self.is_square_attacked(king_position, color)

    def find_king(self, color):
        king_symbol = 'K' if color == 'white' else 'k'
        king_bitboard = self.bitboards[king_symbol]
        if king_bitboard:
            return king_bitboard.bit_length() - 1
        return None

    def generate_castling_moves(self, color):
        moves = []
        row = 0 if color == 'white' else 7
        king_position = self.find_king(color)

        if not self.king_moved[color]:
            # Kingside castling
            if not self.rook_moved[color][1] and not self.occupied & (1 << (king_position + 1)) and not self.occupied & (1 << (king_position + 2)):
                if not self.is_square_attacked(king_position, color) and not self.is_square_attacked(king_position + 1, color) and not self.is_square_attacked(king_position + 2, color):
                    moves.append((king_position, king_position + 2))

            # Queenside castling
            if not self.rook_moved[color][0] and not self.occupied & (1 << (king_position - 1)) and not self.occupied & (1 << (king_position - 2)) and not self.occupied & (1 << (king_position - 3)):
                if not self.is_square_attacked(king_position, color) and not self.is_square_attacked(king_position - 1, color) and not self.is_square_attacked(king_position - 2, color):
                    moves.append((king_position, king_position - 2))

        return moves

    def generate_moves(self, color):
        moves = []
        piece_types = ['P', 'N', 'B', 'R', 'Q', 'K'] if color == 'white' else ['p', 'n', 'b', 'r', 'q', 'k']

        for piece in piece_types:
            bitboard = self.bitboards[piece]
            while bitboard:
                position = bitboard.bit_length() - 1
                if piece.lower() == 'p':
                    moves.extend(self.generate_pawn_moves(position, color))
                elif piece.lower() == 'n':
                    moves.extend(self.generate_knight_moves(position))
                elif piece.lower() == 'b':
                    moves.extend(self.generate_bishop_moves(position))
                elif piece.lower() == 'r':
                    moves.extend(self.generate_rook_moves(position))
                elif piece.lower() == 'q':
                    moves.extend(self.generate_queen_moves(position))
                elif piece.lower() == 'k':
                    moves.extend(self.generate_king_moves(position))
                bitboard &= ~(1 << position)

        # Add castling moves
        moves.extend(self.generate_castling_moves(color))

        return moves

    def generate_pawn_moves(self, position, color):
        moves = []
        direction = -8 if color == 'white' else 8
        start_row = 6 if color == 'white' else 1
        promotion_row = 0 if color == 'white' else 7

        # Single move forward
        if not self.occupied & (1 << (position + direction)):
            moves.append((position, position + direction))
            # Double move from starting position
            if (position // 8) == start_row and not self.occupied & (1 << (position + 2 * direction)):
                moves.append((position, position + 2 * direction))

        # Captures
        for capture_direction in [-9, -7] if color == 'white' else [7, 9]:
            capture_pos = position + capture_direction
            if 0 <= capture_pos < 64 and self.occupied & (1 << capture_pos):
                if self.get_piece_at(capture_pos).islower() if color == 'white' else self.get_piece_at(capture_pos).isupper():
                    moves.append((position, capture_pos))

        # Promotion
        moves = [(start, end) for start, end in moves if end // 8 != promotion_row]

        return moves

    def generate_knight_moves(self, position):
        moves = []
        knight_moves = self.knight_moves[position]
        while knight_moves:
            target = knight_moves.bit_length() - 1
            if not self.occupied & (1 << target) or self.get_piece_at(target).islower() != self.get_piece_at(position).islower():
                moves.append((position, target))
            knight_moves &= ~(1 << target)
        return moves

    def generate_bishop_moves(self, position):
        moves = []
        for direction in [9, 7, -9, -7]:
            current_pos = position
            while True:
                current_pos += direction
                if not (0 <= current_pos < 64) or (current_pos % 8 == 0 and direction in [7, -9]) or (current_pos % 8 == 7 and direction in [9, -7]):
                    break
                if self.occupied & (1 << current_pos):
                    if self.get_piece_at(current_pos).islower() != self.get_piece_at(position).islower():
                        moves.append((position, current_pos))
                    break
                moves.append((position, current_pos))
        return moves

    def generate_rook_moves(self, position):
        moves = []
        for direction in [8, -8, 1, -1]:
            current_pos = position
            while True:
                current_pos += direction
                if not (0 <= current_pos < 64) or (current_pos % 8 == 0 and direction == -1) or (current_pos % 8 == 7 and direction == 1):
                    break
                if self.occupied & (1 << current_pos):
                    if self.get_piece_at(current_pos).islower() != self.get_piece_at(position).islower():
                        moves.append((position, current_pos))
                    break
                moves.append((position, current_pos))
        return moves

    def generate_queen_moves(self, position):
        return self.generate_bishop_moves(position) + self.generate_rook_moves(position)

    def generate_king_moves(self, position):
        moves = []
        king_moves = self.king_moves[position]
        while king_moves:
            target = king_moves.bit_length() - 1
            if not self.occupied & (1 << target) or self.get_piece_at(target).islower() != self.get_piece_at(position).islower():
                moves.append((position, target))
            king_moves &= ~(1 << target)
        return moves


    def print_board(self):
        for rank in range(8):
            line = ""
            for file in range(8):
                position = rank * 8 + file
                piece = self.get_piece_at(position)
                line += (piece if piece else '.') + " "
            print(line)
        print("\n")

def create_piece_from_symbol(symbol):
        color = 'white' if symbol.isupper() else 'black'
        symbol = symbol.lower()
        if symbol == 'p':
            return Pawn(color)
        elif symbol == 'r':
            return Rook(color)
        elif symbol == 'n':
            return Knight(color)
        elif symbol == 'b':
            return Bishop(color)
        elif symbol == 'q':
            return Queen(color)
        elif symbol == 'k':
            return King(color)
        return None