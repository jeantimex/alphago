"""
Territory evaluation module for the Go game implementation.
Evaluates territory control and influence on the board.
"""

import numpy as np
from .constants import BLACK, WHITE, EMPTY

class TerritoryEvaluator:
    def __init__(self, board):
        """
        Initialize a new territory evaluator.
        
        Args:
            board (Board): The game board
        """
        self.board = board
        self.territory_map = None
        self.influence_map = None
        self.potential_territory = True  # Enable potential territory evaluation by default
    
    def evaluate(self):
        """
        Evaluate the territory control and influence on the board.
        Uses a sophisticated algorithm based on standard Go rules and influence propagation.
        
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
        
        # Step 1: Mark stones on the board with strong influence
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
        # Increase iterations for more potential territory evaluation
        propagation_iterations = 8 if self.potential_territory else 3
        
        # Create a distance-based decay matrix for influence propagation
        decay_matrix = np.ones((3, 3), dtype=float)
        decay_matrix[0, 0] = decay_matrix[0, 2] = decay_matrix[2, 0] = decay_matrix[2, 2] = 0.2  # Diagonals
        decay_matrix[0, 1] = decay_matrix[1, 0] = decay_matrix[1, 2] = decay_matrix[2, 1] = 0.4  # Adjacents
        decay_matrix[1, 1] = 0  # Center (will be handled separately)
        
        for _ in range(propagation_iterations):
            new_territory_map = territory_map.copy()
            
            for y in range(size):
                for x in range(size):
                    if self.board.get_stone(x, y) == EMPTY:
                        # For potential territory, we use a more sophisticated influence propagation
                        if self.potential_territory:
                            influence_sum = 0
                            weight_sum = 0
                            
                            # Apply the decay matrix for influence propagation
                            for dy in range(-1, 2):
                                for dx in range(-1, 2):
                                    ny, nx = y + dy, x + dx
                                    if 0 <= ny < size and 0 <= nx < size and (dy != 0 or dx != 0):
                                        # Weight based on distance and current influence
                                        weight = decay_matrix[dy+1, dx+1]
                                        influence = territory_map[ny, nx]
                                        
                                        # Stones have stronger influence than empty spaces
                                        if self.board.get_stone(nx, ny) != EMPTY:
                                            weight *= 2
                                        
                                        influence_sum += influence * weight
                                        weight_sum += weight
                            
                            if weight_sum > 0:
                                # Blend current value with weighted neighborhood influence
                                current_weight = 0.6  # Weight for current value
                                neighbor_weight = 0.4  # Weight for neighbors
                                
                                new_value = (
                                    current_weight * territory_map[y, x] +
                                    neighbor_weight * (influence_sum / weight_sum)
                                )
                                
                                new_territory_map[y, x] = new_value
                        else:
                            # Original simpler influence propagation
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
    
    def calculate_score(self, captured_stones):
        """
        Calculate the score for each player.
        This is a simplified scoring system (area scoring).
        
        Args:
            captured_stones: Dictionary with the count of captured stones by each player
        
        Returns:
            dict: Dictionary with the score for each player
        """
        territory = self.get_territory_ownership()
        stones = self._count_stones()
        
        black_score = stones[BLACK] + territory[BLACK]
        white_score = stones[WHITE] + territory[WHITE]
        
        # Add komi (compensation for black's advantage of going first)
        # Standard komi is 6.5 points
        white_score += 6.5
        
        return {BLACK: black_score, WHITE: white_score}
    
    def _count_stones(self):
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
    
    def set_potential_territory(self, enabled):
        """
        Enable or disable potential territory evaluation.
        
        Args:
            enabled (bool): Whether to enable potential territory evaluation
        """
        self.potential_territory = enabled
