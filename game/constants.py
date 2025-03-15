"""
Constants used throughout the Go game implementation.
"""

# Board size (standard sizes are 9x9, 13x13, 19x19)
BOARD_SIZE = 19

# Stone colors
EMPTY = 0
BLACK = 1
WHITE = 2

# Territory types
BLACK_TERRITORY = BLACK
WHITE_TERRITORY = WHITE
POTENTIAL_BLACK_TERRITORY = 3
POTENTIAL_WHITE_TERRITORY = 4

# UI constants
CELL_SIZE = 30  # Size of each cell in pixels
BOARD_PADDING = 40  # Padding around the board in pixels

# Territory visualization colors (semi-transparent)
BLACK_TERRITORY_COLOR = (0, 0, 0, 80)  # Black with alpha
WHITE_TERRITORY_COLOR = (255, 255, 255, 80)  # White with alpha
POTENTIAL_BLACK_TERRITORY_COLOR = (0, 0, 0, 40)  # Light black with alpha
POTENTIAL_WHITE_TERRITORY_COLOR = (255, 255, 255, 40)  # Light white with alpha

# Button dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
