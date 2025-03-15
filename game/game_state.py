"""
Game state module for the Go game implementation.
Manages the game flow, player turns, and game rules.
"""

from .constants import BLACK, WHITE, EMPTY

class GameState:
    def __init__(self, board):
        """
        Initialize a new game state.
        
        Args:
            board (Board): The game board
        """
        self.board = board
        self.current_player = BLACK  # Black goes first
        self.pass_count = 0  # Count of consecutive passes
        self.move_history = []  # History of moves
        self.captured_stones = {BLACK: 0, WHITE: 0}  # Count of captured stones by each player
    
    def place_stone(self, x, y):
        """
        Place a stone at the specified position for the current player.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        
        Returns:
            bool: True if the move was valid, False otherwise
        """
        # Count stones before the move to calculate captures
        stones_before = self.count_stones()
        
        # Try to place the stone
        if not self.board.place_stone(x, y, self.current_player):
            return False
        
        # Record the move
        self.move_history.append((x, y, self.current_player))
        
        # Reset pass count
        self.pass_count = 0
        
        # Count stones after the move to calculate captures
        stones_after = self.count_stones()
        
        # Calculate captures
        opponent = WHITE if self.current_player == BLACK else BLACK
        captured = stones_before[opponent] - stones_after[opponent]
        if captured > 0:
            self.captured_stones[self.current_player] += captured
        
        # Switch player
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        
        return True
    
    def pass_turn(self):
        """
        Pass the current player's turn.
        
        Returns:
            bool: True if the game is over (two consecutive passes), False otherwise
        """
        self.pass_count += 1
        self.move_history.append(("pass", self.current_player))
        
        # Switch player
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        
        # Check if the game is over (two consecutive passes)
        return self.pass_count >= 2
    
    def is_game_over(self):
        """
        Check if the game is over.
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        return self.pass_count >= 2
    
    def count_stones(self):
        """
        Count the number of stones of each color on the board.
        
        Returns:
            dict: Dictionary with the count of stones for each color
        """
        black_count = 0
        white_count = 0
        
        for y in range(self.board.size):
            for x in range(self.board.size):
                stone = self.board.get_stone(x, y)
                if stone == BLACK:
                    black_count += 1
                elif stone == WHITE:
                    white_count += 1
        
        return {BLACK: black_count, WHITE: white_count}
    
    def calculate_score(self):
        """
        Calculate the score for each player.
        This is a simplified scoring system (area scoring).
        
        Returns:
            dict: Dictionary with the score for each player
        """
        territory = self.calculate_territory()
        stones = self.count_stones()
        
        black_score = stones[BLACK] + territory[BLACK]
        white_score = stones[WHITE] + territory[WHITE]
        
        # Add komi (compensation for black's advantage of going first)
        # Standard komi is 6.5 points
        white_score += 6.5
        
        return {BLACK: black_score, WHITE: white_score}
    
    def calculate_territory(self):
        """
        Calculate the territory controlled by each player.
        This is a simplified territory calculation.
        
        Returns:
            dict: Dictionary with the territory for each player
        """
        # Create a copy of the board to mark territory
        territory_board = self.board.board.copy()
        
        # Find empty spaces and determine which player controls them
        black_territory = 0
        white_territory = 0
        
        # For each empty intersection, check if it's surrounded by one color
        for y in range(self.board.size):
            for x in range(self.board.size):
                if territory_board[y, x] == EMPTY:
                    # Check if this empty space is territory
                    surrounded_by = self.check_surrounded_by(x, y)
                    if surrounded_by == BLACK:
                        black_territory += 1
                    elif surrounded_by == WHITE:
                        white_territory += 1
        
        return {BLACK: black_territory, WHITE: white_territory}
    
    def check_surrounded_by(self, x, y):
        """
        Check if an empty intersection is surrounded by stones of one color.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        
        Returns:
            int: BLACK if surrounded by black, WHITE if surrounded by white, 
                 EMPTY if not surrounded or surrounded by both colors
        """
        # This is a simplified version that just checks immediate neighbors
        # A more accurate version would use flood fill to find connected empty spaces
        black_count = 0
        white_count = 0
        
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < self.board.size and 0 <= ny < self.board.size:
                stone = self.board.get_stone(nx, ny)
                if stone == BLACK:
                    black_count += 1
                elif stone == WHITE:
                    white_count += 1
        
        # If all neighbors are of one color, it's territory of that color
        if black_count > 0 and white_count == 0:
            return BLACK
        elif white_count > 0 and black_count == 0:
            return WHITE
        else:
            return EMPTY
    
    def current_player_name(self):
        """
        Get the name of the current player.
        
        Returns:
            str: "Black" or "White"
        """
        return "Black" if self.current_player == BLACK else "White"
