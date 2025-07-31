from manim import *
from typing import Tuple
import numpy as np
import os

SQUARE_Z = 0
HIGHLIGHT_Z = 1
PIECE_Z = 2

class ChessBoard(Mobject):
    def __init__(self, fen, **kwargs):
        super().__init__(**kwargs)
        self.fen_rows, self.dims = self._read_fen(fen)
        self.icons = [[None for _ in range(self.dims[1])] for _ in range(self.dims[0])]
        self.squares = [[None for _ in range(self.dims[1])] for _ in range(self.dims[0])]
        self.draw_empty_board()
        self.draw_pieces()

    def move_piece(self, i, j, n, m):
        # Get the piece at the starting position
        piece_to_move = self.icons[i][j]
    
        # If there's no piece to move, return an empty animation list
        if piece_to_move is None:
            return []
    
        animations = []
    
        # If the destination square is occupied, shrink the piece at the destination
        piece_at_destination = self.icons[n][m]
        if piece_at_destination is not None:
            animations.append(FadeOut(piece_at_destination))  # Shrink the piece at destination
    
        # Move the piece to the target square (n, m)
        piece_to_move.generate_target()
        piece_to_move.target.move_to(self.squares[n][m].get_center())  # Move piece to new position
        animations.append(MoveToTarget(piece_to_move))  # Add the move animation
    
        # Update the icon positions in the 'icons' array
        self.icons[i][j] = None 
        self.icons[n][m] = piece_to_move
         # Clear the old position

        # Handle pawn promotion (if applicable)
        promotion_animations = self.handle_pawn_promotion(piece_to_move, n, m)
        if promotion_animations:
            animations.extend(promotion_animations)
    
        return animations

    def add_arrow(self, i, j, dx, dy):
        graphical_arrow = Arrow((DOWN * i + RIGHT * j), (DOWN * (i + dx) + RIGHT * (j + dy)), color=BLUE, stroke_width=5,   max_stroke_width_to_length_ratio=10, max_tip_length_to_length_ratio=0.5)
        circle = Circle(0.25, stroke_width=DEFAULT_STROKE_WIDTH*1).shift((DOWN * (i + dx) + RIGHT * (j + dy)))
        group = Group(circle, graphical_arrow)
        self.add(group)

    def add_highlight(self, i, j, color):
        square = Square(0.999, stroke_width=0, fill_color=color, fill_opacity=0.7)
        square.move_to(self.squares[i][j])
        self.add(square)
        
    def set_piece_opacities(self, opacities: np.ndarray):
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                icon = self.icons[i][j]
                if icon is not None:
                    alpha = opacities[i, j]
                    alpha_mask = np.copy(icon.pixel_array[:, :, 3]) != 0
                    icon.pixel_array[:, :, 3] = int(255 * alpha) * alpha_mask

    def _piece_to_icon(self, c):
        prefix = "w" if c.isupper() else "b"
        prefix = prefix if not c.isspace() else ""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        piece_path = os.path.join(dir_path, "png_pieces/{}.png".format(prefix + c.upper()))
        icon = ImageMobject(piece_path)
        icon.set_x(0)
        icon.set_y(0)
        icon.scale(0.27)
        icon.piece_path = piece_path 
    
        if c.lower() == "k":
            icon.shift(UP * 0.035)
    
        return icon

    def _read_fen(self, fen):
        if " " in fen:
            fen = fen.split(" ")[0]
        
        rows = fen.split("/")


        for i, row in enumerate(rows):
            new_row = ""
            for c in row:
                if c in "123456789":
                    new_row += " " * int(c)
                else:
                    new_row += c
            rows[i] = new_row
        dims = (len(rows), max([len(row) for row in rows]))
        return rows, dims


    def draw_pieces(self):
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if not self.fen_rows[i][j].isspace():  # Ignore empty squares
                    piece = self.fen_rows[i][j]  # Get the piece character (e.g., 'r', 'P', etc.)
                    icon = self._piece_to_icon(piece)  # Convert the piece to an icon (ImageMobject)
                    icon.shift(i * DOWN + j * RIGHT).set_z_index(PIECE_Z)  # Position it on the board
                    self.icons[i][j] = icon  # Store the piece in the icons array

        for row in self.icons:
            for icon in row:
                if icon is not None:
                    self.add(icon)

    def draw_empty_board(self):
        board = []
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                color = "#ffffff" if ((i + j + 1) % 2) == 0 else "#69923e"
                square = Square(0.999, stroke_color=BLACK, stroke_width=0)
                square.set_fill(color, 1)
                square.shift(i * DOWN + j * RIGHT)
                square.set_z(SQUARE_Z)
                self.squares[i][j] = square

        for row in self.squares:
            for sq in row:
                self.add(sq)

    def animate_move(self,piece_from,piece_to):
        fade_out, movement = board.move_piece(piece_from[0], piece_from[1], piece_to[0], piece_to[1])
        if fade_out is not None:
            self.play(fade_out)
        self.play(movement)
        board.icons[piece_from[0]][piece_from[1]] = None

    def get_piece_type_by_icon(self, i, j):
        piece_icon = self.icons[i][j]
        if piece_icon is None:
            return None
        icon_path = piece_icon.piece_path  
        piece_filename = os.path.basename(icon_path)
        color_char = piece_filename[0]
        if color_char == 'w':
            color = "White"
        elif color_char == 'b':
            color = "Black"
        else:
            color = "Unknown"

        piece_char = piece_filename[1].upper() 
        if piece_char == 'P':
            piece_type = 'Pawn'
        elif piece_char == 'R':
            piece_type = 'Rook'
        elif piece_char == 'N':
            piece_type = 'Knight'
        elif piece_char == 'B':
            piece_type = 'Bishop'
        elif piece_char == 'Q':
            piece_type = 'Queen'
        elif piece_char == 'K':
            piece_type = 'King'
        else:
            piece_type = "Unknown"
        
        return color, piece_type
        
    def handle_pawn_promotion(self, piece_to_move, i, j):
        piece_char = self.get_piece_type_by_icon(i, j)
        
        if piece_char is None:
            return []
    
        if piece_char[0] == 'White' and i == 0 and piece_char[1] == 'Pawn':
            new_piece = self._piece_to_icon("Q")  
            new_piece.scale(0.5)
            new_piece.move_to(self.squares[i][j].get_center())  
            self.icons[i][j] = new_piece  
            return [FadeOut(piece_to_move), FadeIn(new_piece)]

        elif piece_char[0] == 'Black' and i == 7 and piece_char[1] == 'Pawn':
            new_piece = self._piece_to_icon("q")  
            new_piece.scale(0.5)
            new_piece.move_to(self.squares[i][j].get_center()) 
            self.icons[i][j] = new_piece
            return [FadeOut(piece_to_move), FadeIn(new_piece)]
        
        return []
    
     
    
    
    
    
    
            