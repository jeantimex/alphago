"""
Game state module for the Go game implementation.
Manages the game flow, player turns, and game rules.
"""

import numpy as np
from .constants import BLACK, WHITE, EMPTY
from .territory import TerritoryEvaluator

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
        self.territory_evaluator = TerritoryEvaluator(board)  # Territory evaluator
    
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
        
        # Reset territory evaluator maps
        self.territory_evaluator = TerritoryEvaluator(self.board)
        
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
        return self.territory_evaluator.calculate_score(self.captured_stones)
    
    def evaluate_territory(self):
        """
        Evaluate the territory control and influence on the board.
        
        Returns:
            tuple: (territory_map, influence_map)
        """
        return self.territory_evaluator.evaluate()
    
    def get_territory_ownership(self):
        """
        Get the territory ownership based on the influence map.
        
        Returns:
            dict: Dictionary with counts of territory for each player and neutral
        """
        return self.territory_evaluator.get_territory_ownership()
    
    def get_detailed_territory(self):
        """
        Get detailed territory information including coordinates and influence values.
        
        Returns:
            dict: Dictionary with lists of (point, influence) tuples for each player
        """
        # Make sure territory has been evaluated
        if self.territory_evaluator.territory_map is None:
            self.territory_evaluator.evaluate()
        
        black_territory = []
        white_territory = []
        
        for y in range(self.board.size):
            for x in range(self.board.size):
                if self.board.get_stone(x, y) == EMPTY:
                    influence = self.territory_evaluator.territory_map[y, x]
                    if influence > 0.5:  # Black territory
                        black_territory.append(((x, y), influence))
                    elif influence < -0.5:  # White territory
                        white_territory.append(((x, y), influence))
        
        return {
            'black': black_territory,
            'white': white_territory
        }
    
    @property
    def territory_map(self):
        """Get the territory map from the evaluator."""
        return self.territory_evaluator.territory_map
    
    @property
    def influence_map(self):
        """Get the influence map from the evaluator."""
        return self.territory_evaluator.influence_map
    
    def current_player_name(self):
        """
        Get the name of the current player.
        
        Returns:
            str: "Black" or "White"
        """
        return "Black" if self.current_player == BLACK else "White"
