"""
Territory evaluation module for the Go game implementation.
Provides algorithms to evaluate territory control and influence on the board.
"""

import numpy as np
from .constants import BLACK, WHITE, EMPTY

class TerritoryEvaluator:
    """
    Class for evaluating territory in a Go game.
    Implements various algorithms for territory calculation and visualization.
    """
    
    def __init__(self, board):
        """
        Initialize the territory evaluator.
        
        Args:
            board: The game board object
        """
        self.board = board
        self.territory_map = None
        self.influence_map = None
    
    def evaluate(self):
        """
        Evaluate the territory control and influence on the board.
        Uses a sophisticated algorithm based on standard Go rules.
        
        Returns:
            tuple: (territory_map, influence_map)
                territory_map: 2D numpy array where:
                    positive values indicate BLACK territory/influence
                    negative values indicate WHITE territory/influence
                    the magnitude indicates confidence (higher = more confident)
                influence_map: 2D numpy array with normalized influence values for visualization
        """
        size = self.board.size
        # Initialize maps
        territory_map = np.zeros((size, size), dtype=float)
        influence_map = np.zeros((size, size), dtype=float)
        
        # Step 1: Mark stones on the board
        for y in range(size):
            for x in range(size):
                stone = self.board.get_stone(x, y)
                if stone == BLACK:
                    territory_map[y, x] = 10  # Strong black influence
                elif stone == WHITE:
                    territory_map[y, x] = -10  # Strong white influence
        
        # Step 2: Identify empty spaces and perform flood fill to determine territories
        visited = np.zeros((size, size), dtype=bool)
        
        for y in range(size):
            for x in range(size):
                if self.board.get_stone(x, y) == EMPTY and not visited[y, x]:
                    # Perform flood fill from this empty intersection
                    empty_points = []
                    border_stones = set()
                    
                    self._flood_fill(x, y, empty_points, border_stones, visited)
                    
                    # Check if this territory is surrounded by one color
                    black_borders = sum(1 for stone in border_stones if stone == BLACK)
                    white_borders = sum(1 for stone in border_stones if stone == WHITE)
                    
                    territory_value = 0
                    if black_borders > 0 and white_borders == 0:
                        # Black territory
                        territory_value = 5  # Strong confidence
                    elif white_borders > 0 and black_borders == 0:
                        # White territory
                        territory_value = -5  # Strong confidence
                    else:
                        # Neutral or contested territory
                        # Calculate relative influence based on surrounding stones
                        if black_borders > 0 and white_borders > 0:
                            ratio = black_borders / (black_borders + white_borders)
                            # Scale from -2 to 2 for contested territories
                            territory_value = (ratio - 0.5) * 4
                    
                    # Assign territory value to all points in this empty region
                    for px, py in empty_points:
                        territory_map[py, px] = territory_value
        
        # Step 3: Propagate influence from strong territories to weaker ones
        # This creates a more gradual transition in influence
        for _ in range(3):  # Multiple iterations to smooth influence
            new_territory_map = territory_map.copy()
            
            for y in range(size):
                for x in range(size):
                    if self.board.get_stone(x, y) == EMPTY:
                        # Calculate influence from neighbors
                        neighbors_influence = 0
                        neighbor_count = 0
                        
                        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                            if 0 <= nx < size and 0 <= ny < size:
                                neighbors_influence += territory_map[ny, nx]
                                neighbor_count += 1
                        
                        if neighbor_count > 0:
                            # Blend current value with neighbors (weighted average)
                            current_weight = 0.7  # Weight for current value
                            neighbor_weight = 0.3  # Weight for neighbors' average
                            
                            new_value = (
                                current_weight * territory_map[y, x] +
                                neighbor_weight * (neighbors_influence / neighbor_count)
                            )
                            
                            new_territory_map[y, x] = new_value
            
            territory_map = new_territory_map
        
        # Normalize the influence map for visualization
        abs_max = max(np.max(np.abs(territory_map)), 1)  # Avoid division by zero
        influence_map = territory_map / abs_max
        
        # Store the maps
        self.territory_map = territory_map
        self.influence_map = influence_map
        
        return territory_map, influence_map
    
    def _flood_fill(self, x, y, empty_points, border_stones, visited):
        """
        Perform flood fill from an empty intersection to find connected empty points
        and their bordering stones.
        
        Args:
            x, y: Starting coordinates
            empty_points: List to collect empty points
            border_stones: Set to collect bordering stone colors
            visited: Boolean array to track visited intersections
        """
        # Check if out of bounds or already visited
        if (x < 0 or x >= self.board.size or 
            y < 0 or y >= self.board.size or 
            visited[y, x]):
            return
        
        # Check the current point
        stone = self.board.get_stone(x, y)
        
        if stone == EMPTY:
            # Mark as visited and add to empty points
            visited[y, x] = True
            empty_points.append((x, y))
            
            # Continue flood fill in all four directions
            self._flood_fill(x+1, y, empty_points, border_stones, visited)
            self._flood_fill(x-1, y, empty_points, border_stones, visited)
            self._flood_fill(x, y+1, empty_points, border_stones, visited)
            self._flood_fill(x, y-1, empty_points, border_stones, visited)
        else:
            # This is a border stone, add its color to the set
            border_stones.add(stone)
    
    def get_territory_ownership(self):
        """
        Get the territory ownership based on the influence map.
        
        Returns:
            dict: Dictionary with counts of territory for each player and neutral
        """
        if self.territory_map is None:
            self.evaluate()
        
        black_territory = 0
        white_territory = 0
        neutral_territory = 0
        
        for y in range(self.board.size):
            for x in range(self.board.size):
                if self.board.get_stone(x, y) == EMPTY:
                    influence = self.territory_map[y, x]
                    if influence > 0.5:  # Strong black influence - increased threshold
                        black_territory += 1
                    elif influence < -0.5:  # Strong white influence - increased threshold
                        white_territory += 1
                    else:  # Neutral or contested
                        neutral_territory += 1
        
        return {
            BLACK: black_territory,
            WHITE: white_territory,
            EMPTY: neutral_territory
        }
    
    def calculate_score(self, captured_stones=None):
        """
        Calculate the score for each player using territory and captured stones.
        This is a simplified scoring system (area scoring).
        
        Args:
            captured_stones: Dictionary with the count of captured stones for each player
        
        Returns:
            dict: Dictionary with the score for each player
        """
        if captured_stones is None:
            captured_stones = {BLACK: 0, WHITE: 0}
        
        territory = self.get_territory_ownership()
        
        # Count stones on the board
        black_stones = 0
        white_stones = 0
        
        for y in range(self.board.size):
            for x in range(self.board.size):
                stone = self.board.get_stone(x, y)
                if stone == BLACK:
                    black_stones += 1
                elif stone == WHITE:
                    white_stones += 1
        
        # Calculate scores
        black_score = black_stones + territory[BLACK] + captured_stones[BLACK]
        white_score = white_stones + territory[WHITE] + captured_stones[WHITE]
        
        # Add komi (compensation for black's advantage of going first)
        # Standard komi is 6.5 points
        white_score += 6.5
        
        return {BLACK: black_score, WHITE: white_score}
