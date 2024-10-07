# main.py
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import simpledialog
from chess.chess_board import ChessBoard
from chess.pieces import Queen, Rook, Bishop, Knight, Pawn
from chess.ai.random_ai import RandomAI
from chess.ai.minimax_ai import MinimaxAI
from chess.ai.minimax_bit_ai import MinimaxBitAI
from chess.theme import Theme

# Constants
SQUARE_SIZE = 120
ROWS, COLS = 8, 8
WIDTH, HEIGHT = SQUARE_SIZE * COLS, SQUARE_SIZE * ROWS

# Colors
WHITE = "#F0D9B5"
BLACK = "#B58863"
HIGHLIGHT = "#1E90FF"
SELECTED = "#FFD700"  # Gold color for selected piece
MENU_BG = "#333333"
BUTTON_BG = "#555555"
BUTTON_FG = "#FFFFFF"
LAST_MOVE_HIGHLIGHT = "#90EE90"

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.theme = Theme.DEFAULT
        self.root.title("Chess")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.flipped = True
        self.chess_board = ChessBoard(flipped=self.flipped)
        self.selected_piece = None
        self.checkmate_button = None
        self.valid_moves = []
        self.piece_images = self.load_images()
        self.main_menu_open = False
        self.main_menu = None
        self.create_main_menu_button()
        self.current_turn = 'white'  # Track whose turn it is
        self.ai = None
        self.last_move = None
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<f>", self.flip_board)

    def load_images(self):
        images = {}
        piece_names = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        base_path = self.theme.value
        scaler = 0.7
        if self.theme == Theme.DEFAULT:
            scaler = 0.8
        for piece in piece_names:
            # Load and scale white pieces
            white_image = Image.open(f'{base_path}w_{piece}.png')
            white_image = white_image.resize((int(scaler * SQUARE_SIZE), int(scaler * SQUARE_SIZE)), Image.LANCZOS)
            images[f'white_{piece}'] = ImageTk.PhotoImage(white_image)

            # Load and scale black pieces
            black_image = Image.open(f'{base_path}b_{piece}.png')
            black_image = black_image.resize((int(scaler * SQUARE_SIZE), int(scaler * SQUARE_SIZE)), Image.LANCZOS)
            images[f'black_{piece}'] = ImageTk.PhotoImage(black_image)

        return images

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(ROWS):
            for col in range(COLS):
                # Determine the color of the square
                color = WHITE if (row + col) % 2 == 0 else BLACK
                

                if self.last_move:
                    start, end = self.last_move
                    if(row, col) == start or (row, col) == end:
                        color = LAST_MOVE_HIGHLIGHT

                # Draw the square
                self.canvas.create_rectangle(col * SQUARE_SIZE, row * SQUARE_SIZE,
                                            (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                                            fill=color)

                if self.selected_piece == (row, col):
                    self.canvas.create_rectangle(col * SQUARE_SIZE, row * SQUARE_SIZE,
                                             (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                                             fill=SELECTED, width=3)

                # Draw the piece
                piece = self.chess_board.board[row][col]
                if piece:
                    piece_name = {
                        'P': 'pawn',
                        'R': 'rook',
                        'N': 'knight',
                        'B': 'bishop',
                        'Q': 'queen',
                        'K': 'king'
                    }[piece.symbol]
                    piece_color = 'white' if piece.color == 'white' else 'black'
                    piece_image = self.piece_images[f'{piece_color}_{piece_name}']
                    self.canvas.create_image(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                            row * SQUARE_SIZE + SQUARE_SIZE // 2,
                                            image=piece_image)

                # Highlight valid moves
                if (row, col) in self.valid_moves:
                    self.canvas.create_rectangle(col * SQUARE_SIZE, row * SQUARE_SIZE,
                                                (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                                                outline=HIGHLIGHT, width=3)

    def on_click(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE

        if self.chess_board.is_checkmate(self.current_turn):
            print(f"Checkmate! {self.current_turn} loses.")
            self.show_main_menu()   
            return
        elif self.chess_board.is_stalemate(self.current_turn):
            print("Stalemate! The game is a draw.")
            self.show_main_menu()
            return

        if self.selected_piece:
            if (row, col) == self.selected_piece:
                print("Deselecting bitch")
                self.selected_piece = None
                self.valid_moves = []
            if (row, col) in self.valid_moves:
                self.chess_board.update_board((self.selected_piece, (row, col)))

                self.last_move = (self.selected_piece, (row, col))
                piece = self.chess_board.board[row][col]
                if isinstance(piece, Pawn) and (row == 0 or row == 7):
                    self.valid_moves = []
                    self.prompt_promotion(row, col)
                    return
                if self.chess_board.is_checkmate(self.current_turn):
                    print(f"Checkmate! {self.current_turn} loses.")
                    self.show_main_menu()
                    return
                elif self.chess_board.is_stalemate(self.current_turn):
                    print("Stalemate! The game is a draw.")
                    self.show_main_menu()
                    return
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                if self.ai and self.current_turn == self.ai.color:
                    self.ai_move()  
            self.selected_piece = None
            self.valid_moves = []

        else:
            piece = self.chess_board.board[row][col]
            if piece and piece.color == self.current_turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.chess_board.get_valid_moves((row, col), self.flipped)
                # Filter out moves that leave the king in check
                self.valid_moves = [move for move in self.valid_moves if not self.move_leaves_king_in_check((row, col), move)]
        self.draw_board()

    def ai_move(self):
        self.chess_board.print_board_state()
        move, promotion_choice = self.ai.make_move(self.chess_board, self.flipped)
        if move:
            start, end = move
            piece = self.chess_board.board[start[0]][start[1]]

            if promotion_choice and isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
                # Apply promotion
                self.chess_board.board[end[0]][end[1]] = promotion_choice(piece.color)
                self.chess_board.board[start[0]][start[1]] = None
            else:
                self.chess_board.update_board(move)  # Apply the move

            self.last_move = move
            if self.chess_board.is_checkmate(self.current_turn):
                print(f"Checkmate! {self.current_turn} loses.")
                self.show_main_menu()
                return
            elif self.chess_board.is_stalemate(self.current_turn):
                print("Stalemate! The game is a draw.")
                self.show_main_menu()
                return
            self.current_turn = 'white' if self.current_turn == 'black' else 'black'
        self.draw_board()

    def prompt_promotion(self, row, col):
        promotion_window = tk.Toplevel(self.root)
        promotion_window.title("Promote Pawn")
        promotion_window.geometry("200x100")

        current_color = self.chess_board.board[row][col].color

        def promote_to(piece_class):
            self.chess_board.board[row][col] = piece_class(current_color)
            print(f"Promoted pawn at ({row}, {col}) to {piece_class.__name__}")
            promotion_window.destroy()
            self.after_promotion()  # Call a method to handle post-promotion actions

        tk.Button(promotion_window, text="Queen", command=lambda: promote_to(Queen)).pack(fill=tk.X)
        tk.Button(promotion_window, text="Rook", command=lambda: promote_to(Rook)).pack(fill=tk.X)
        tk.Button(promotion_window, text="Bishop", command=lambda: promote_to(Bishop)).pack(fill=tk.X)
        tk.Button(promotion_window, text="Knight", command=lambda: promote_to(Knight)).pack(fill=tk.X)

    def after_promotion(self):
        # Check for checkmate after promotion
        if self.chess_board.is_checkmate(self.current_turn):
            print(f"Checkmate! {self.current_turn} loses.")
            self.show_main_menu()
            return
        elif self.chess_board.is_stalemate(self.current_turn):
            print("Stalemate! The game is a draw.")
            self.show_main_menu()
            return

        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        if self.ai and self.current_turn == self.ai.color:
           self.ai_move()

        self.draw_board()

    def move_leaves_king_in_check(self, start, end):
        piece = self.chess_board.board[start[0]][start[1]]
        original_piece = self.chess_board.board[end[0]][end[1]]
        self.chess_board.board[end[0]][end[1]] = piece
        self.chess_board.board[start[0]][start[1]] = None
        in_check = self.chess_board.is_in_check(self.current_turn)
        self.chess_board.board[start[0]][start[1]] = piece
        self.chess_board.board[end[0]][end[1]] = original_piece
        return in_check

    def flip_board(self, event=None):
        self.flipped = not self.flipped
        self.draw_board()

    def create_main_menu_button(self):
        self.main_menu_button = tk.Button(self.root, text="Main Menu", command=self.show_main_menu)
        self.main_menu_button.pack(pady=10)

    def show_main_menu(self):
        if self.main_menu_open:
            return

        self.main_menu_open = True
        menu = tk.Toplevel(self.root)
        self.main_menu = menu
        menu.title("Main Menu")
        menu.geometry("300x400+100+100")  # Set size and position
        menu.configure(bg=MENU_BG)
        menu.protocol("WM_DELETE_WINDOW", self.close_main_menu)

        game_x = self.root.winfo_x()
        game_y = self.root.winfo_y()
        menu.geometry(f"+{game_x + WIDTH + 20}+{game_y}")

        button_style = {"bg": BUTTON_BG, "fg": BUTTON_FG, "font": ("Arial", 12), "relief": "raised", "bd": 2}

        button1 = tk.Button(menu, text="Play with AI", command=self.select_ai, **button_style)
        button1.pack(pady=10, padx=20, fill=tk.X)

        button2 = tk.Button(menu, text="Button 2", command=lambda: print("Button 2 pressed"), **button_style)
        button2.pack(pady=10, padx=20, fill=tk.X)

        button3 = tk.Button(menu, text="Select Theme", command=self.open_theme_selection, **button_style)
        button3.pack(pady=10, padx=20, fill=tk.X)

        play_again = tk.Button(menu, text="Play Again", command=self.restart_game, **button_style)
        play_again.pack(pady=10, padx=20, fill=tk.X)

        close_button = tk.Button(menu, text="Close Main Menu", command=lambda: self.close_main_menu(menu), **button_style)
        close_button.pack(pady=10, padx=20, fill=tk.X)

        exit_button = tk.Button(menu, text="Exit", command=self.root.quit, **button_style)
        exit_button.pack(pady=10, padx=20, fill=tk.X)

    def open_theme_selection(self):
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Select Theme")

        theme_var = tk.StringVar(value=self.theme.name)
        for theme in Theme:
            tk.Radiobutton(theme_window, text=theme.name, variable=theme_var, value=theme.name).pack(anchor=tk.W)

        def apply_theme():
            selected_theme = theme_var.get()
            self.change_theme(selected_theme)
            theme_window.destroy()

        apply_button = tk.Button(theme_window, text="Apply", command=apply_theme)
        apply_button.pack()

    def change_theme(self, selected_theme):
        print(f"Changing theme to: {selected_theme}")  # Debugging statement
        self.theme = Theme[selected_theme]
        self.piece_images = self.load_images()
        self.draw_board()

    def select_ai(self):
        if self.main_menu_open:
            self.close_main_menu(self.main_menu)
        ai_options = {
            "1": RandomAI,
            "2": MinimaxAI,
            "3": MinimaxBitAI
            # Add more AI classes here as you implement them
        }
        ai_names = "\n".join([f"{key}: {ai.__name__}" for key, ai in ai_options.items()])
        selected_ai = simpledialog.askstring("Select AI", f"Choose an AI:\n{ai_names}")

        if selected_ai in ai_options:
            self.ai = ai_options[selected_ai]('black' if self.flipped else 'white')
            self.restart_game()

            if self.ai.color == 'white':
                self.ai_move()
        else:
            print("Invalid selection. Please try again.")

    def close_main_menu(self, menu):
        self.main_menu_open = False
        self.main_menu_button.pack()
        self.main_menu = None
        menu.destroy()

    def restart_game(self):
        self.flipped = not self.flipped
        self.chess_board = ChessBoard(flipped=self.flipped)
        self.current_turn = 'white'
        self.selected_piece = None
        self.valid_moves = []
        self.draw_board()

def main():
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()