def basic_material_evaluation(chess_board, color):
    piece_values = {
        'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
    }
    value = 0
    for row in chess_board.board:
        for piece in row:
            if piece:
                piece_value = piece_values[piece.symbol.upper()]
                value += piece_value if piece.color == color else -piece_value
    return value

def advanced_evaluation(chess_board, color):
    piece_values = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000
    }
    position_values = {
        'P': [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        'N': [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ],
        'B': [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ],
        'R': [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ],
        'Q': [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ],
        'K': [
            [20, 30, 10, 0, 0, 10, 30, 20],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30]
        ]
    }

    value = 0
    for row in range(8):
        for col in range(8):
            piece = chess_board.board[row][col]
            if piece:
                piece_value = piece_values[piece.symbol.upper()]
                position_value = position_values[piece.symbol.upper()][row][col]
                if piece.color == color:
                    value += piece_value + position_value
                else:
                    value -= piece_value + position_value

    # Additional factors
    value += evaluate_king_safety(chess_board, color)
    value += evaluate_pawn_structure(chess_board, color)
    value += evaluate_piece_activity(chess_board, color)
    value += evaluate_center_control(chess_board, color)

    return value

def evaluate_king_safety(chess_board, color):
    king_position = find_king_position(chess_board, color)
    if not king_position:
        return -10000  # King is missing, which should not happen

    # Basic king safety evaluation
    row, col = king_position
    safety_score = 0

    # Check for pawn shield
    pawn_shield_offsets = [(-1, -1), (-1, 0), (-1, 1)] if color == 'white' else [(1, -1), (1, 0), (1, 1)]
    for dr, dc in pawn_shield_offsets:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            piece = chess_board.board[r][c]
            if piece and piece.symbol.lower() == 'p' and piece.color == color:
                safety_score += 10

    # Penalize open files and threats
    if col == 0 or col == 7:  # Edge columns
        safety_score -= 20
    if row == 0 or row == 7:  # Edge rows
        safety_score -= 20

    return safety_score

def evaluate_pawn_structure(chess_board, color):
    pawn_score = 0
    pawn_positions = [(r, c) for r in range(8) for c in range(8) if chess_board.board[r][c] and chess_board.board[r][c].symbol.lower() == 'p' and chess_board.board[r][c].color == color]

    # Evaluate doubled, isolated, and passed pawns
    for row, col in pawn_positions:
        # Doubled pawns
        if any(chess_board.board[r][col] and chess_board.board[r][col].symbol.lower() == 'p' and chess_board.board[r][col].color == color for r in range(row + 1, 8)):
            pawn_score -= 10

        # Isolated pawns
        if not any(chess_board.board[row][c] and chess_board.board[row][c].symbol.lower() == 'p' and chess_board.board[row][c].color == color for c in [col - 1, col + 1] if 0 <= c < 8):
            pawn_score -= 10

        # Passed pawns
        if not any(chess_board.board[r][col] and chess_board.board[r][col].symbol.lower() == 'p' and chess_board.board[r][col].color != color for r in range(row + 1, 8)):
            pawn_score += 20

    return pawn_score

def evaluate_piece_activity(chess_board, color):
    activity_score = 0
    for row in range(8):
        for col in range(8):
            piece = chess_board.board[row][col]
            if piece and piece.color == color:
                # Use get_valid_moves to get all legal moves for the piece
                legal_moves = chess_board.get_valid_moves((row, col))
                activity_score += len(legal_moves)

    return activity_score

def evaluate_center_control(chess_board, color):
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    control_score = 0
    for row, col in center_squares:
        piece = chess_board.board[row][col]
        if piece:
            if piece.color == color:
                control_score += 10
            else:
                control_score -= 10

    return control_score

def find_king_position(chess_board, color):
    for row in range(8):
        for col in range(8):
            piece = chess_board.board[row][col]
            if piece and piece.symbol.lower() == 'k' and piece.color == color:
                return (row, col)
    return None
