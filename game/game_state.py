"""
Game state module for the Go game implementation.
Manages the game flow, player turns, and game rules.
"""

from .constants import BLACK, WHITE, EMPTY
import numpy as np

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
        Uses a more advanced algorithm inspired by KataGo's territory evaluation.
        
        Returns:
            dict: Dictionary with the territory for each player and territory map
        """
        # Create a copy of the board to mark territory
        territory_board = self.board.board.copy()
        territory_map = np.zeros((self.board.size, self.board.size), dtype=int)
        
        # Find empty spaces and determine which player controls them
        black_territory = 0
        white_territory = 0
        
        # First, identify all empty regions using flood fill
        visited = set()
        empty_regions = []
        
        for y in range(self.board.size):
            for x in range(self.board.size):
                if territory_board[y, x] == EMPTY and (x, y) not in visited:
                    # Found a new empty region, flood fill to find all connected empty points
                    region = []
                    border_colors = set()
                    
                    def flood_fill(cx, cy):
                        if (cx, cy) in visited:
                            return
                        
                        if not (0 <= cx < self.board.size and 0 <= cy < self.board.size):
                            return
                        
                        if territory_board[cy, cx] == EMPTY:
                            visited.add((cx, cy))
                            region.append((cx, cy))
                            flood_fill(cx+1, cy)
                            flood_fill(cx-1, cy)
                            flood_fill(cx, cy+1)
                            flood_fill(cx, cy-1)
                        elif territory_board[cy, cx] != EMPTY:
                            # Found a border stone
                            border_colors.add(territory_board[cy, cx])
                    
                    flood_fill(x, y)
                    empty_regions.append((region, border_colors))
        
        # Assign territory based on the border colors of each empty region
        for region, border_colors in empty_regions:
            if len(border_colors) == 1:  # Region is surrounded by stones of one color
                color = list(border_colors)[0]
                for x, y in region:
                    territory_map[y, x] = color  # Mark as territory
                    if color == BLACK:
                        black_territory += 1
                    elif color == WHITE:
                        white_territory += 1
        
        return {
            BLACK: black_territory, 
            WHITE: white_territory,
            'territory_map': territory_map
        }
    
    def calculate_influence(self):
        """
        Calculate influence map for both players based on stone positions.
        This is inspired by KataGo's influence calculation.
        
        Returns:
            numpy.ndarray: Influence map where positive values indicate black influence
                          and negative values indicate white influence
        """
        influence = np.zeros((self.board.size, self.board.size), dtype=float)
        
        # Constants for influence calculation
        DIRECT_INFLUENCE = 1.0
        DIAGONAL_INFLUENCE = 0.5
        DECAY_FACTOR = 0.7
        MAX_DISTANCE = 4  # Maximum distance to propagate influence
        
        # Calculate direct stone influence
        for y in range(self.board.size):
            for x in range(self.board.size):
                stone = self.board.get_stone(x, y)
                if stone == BLACK:
                    influence[y, x] = DIRECT_INFLUENCE
                elif stone == WHITE:
                    influence[y, x] = -DIRECT_INFLUENCE
        
        # Propagate influence
        influence_propagated = influence.copy()
        
        for distance in range(1, MAX_DISTANCE + 1):
            factor = DIRECT_INFLUENCE * (DECAY_FACTOR ** distance)
            
            for y in range(self.board.size):
                for x in range(self.board.size):
                    if self.board.get_stone(x, y) != EMPTY:
                        continue  # Skip non-empty points
                    
                    # Check surrounding points at current distance
                    total_influence = 0
                    count = 0
                    
                    for dy in range(-distance, distance + 1):
                        for dx in range(-distance, distance + 1):
                            # Only consider points exactly at 'distance' away (Manhattan distance)
                            if abs(dx) + abs(dy) != distance:
                                continue
                            
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.board.size and 0 <= ny < self.board.size:
                                total_influence += influence[ny, nx]
                                count += 1
                    
                    if count > 0:
                        influence_propagated[y, x] += (total_influence / count) * factor
        
        return influence_propagated
    
    def get_potential_territory(self):
        """
        Get potential territory based on influence and current territory.
        
        Returns:
            dict: Dictionary with potential territory information
        """
        territory = self.calculate_territory()
        influence = self.calculate_influence()
        
        # Create potential territory map
        potential_territory = np.zeros((self.board.size, self.board.size), dtype=int)
        
        # First, copy definite territory
        potential_territory = territory['territory_map'].copy()
        
        # Then, mark potential territory based on influence
        for y in range(self.board.size):
            for x in range(self.board.size):
                if potential_territory[y, x] == EMPTY:
                    if influence[y, x] > 0.3:  # Threshold for potential black territory
                        potential_territory[y, x] = 3  # Use 3 to represent potential black territory
                    elif influence[y, x] < -0.3:  # Threshold for potential white territory
                        potential_territory[y, x] = 4  # Use 4 to represent potential white territory
        
        # Count potential territory
        black_potential = np.sum(potential_territory == 3)
        white_potential = np.sum(potential_territory == 4)
        
        return {
            'territory_map': territory['territory_map'],
            'potential_territory_map': potential_territory,
            'influence': influence,
            BLACK: territory[BLACK] + black_potential,
            WHITE: territory[WHITE] + white_potential,
            'black_potential': black_potential,
            'white_potential': white_potential
        }
    
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
