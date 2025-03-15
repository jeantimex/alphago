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

# Territory visualization settings
TERRITORY_MARKER_SIZE_RATIO = 0.6  # Size of territory markers relative to cell size (0.0-1.0)
TERRITORY_MARKER_SHAPE = "circle"  # Options: "circle", "square", "diamond"

# Territory visualization colors (RGBA format)
BLACK_TERRITORY_COLOR = (0, 0, 0, 180)  # Black with high alpha
WHITE_TERRITORY_COLOR = (255, 255, 255, 180)  # White with high alpha
POTENTIAL_BLACK_TERRITORY_COLOR = (50, 50, 150, 160)  # Blue-ish for potential black
POTENTIAL_WHITE_TERRITORY_COLOR = (150, 50, 50, 160)  # Red-ish for potential white

# Button dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10

# Territory size slider settings
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 20
MIN_TERRITORY_SIZE = 0.2
MAX_TERRITORY_SIZE = 0.8
DEFAULT_TERRITORY_SIZE = TERRITORY_MARKER_SIZE_RATIO
