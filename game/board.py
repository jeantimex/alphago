"""
Board module for the Go game implementation.
Handles the board representation and basic game mechanics.
"""

import numpy as np
from .constants import EMPTY, BLACK, WHITE

class Board:
    def __init__(self, size):
        """
        Initialize a new Go board.
        
        Args:
            size (int): Size of the board (typically 9, 13, or 19)
        """
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.last_board_state = None  # Used for ko rule checking
    
    def get_stone(self, x, y):
        """
        Get the stone at the specified position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        
        Returns:
            int: Stone color (EMPTY, BLACK, or WHITE)
        """
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.board[y, x]
        return None
    
    def place_stone(self, x, y, color):
        """
        Place a stone on the board.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            color (int): Stone color (BLACK or WHITE)
        
        Returns:
            bool: True if the stone was placed successfully, False otherwise
        """
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        
        if self.board[y, x] != EMPTY:
            return False
        
        # Save the current board state for ko rule checking
        self.last_board_state = self.board.copy()
        
        # Place the stone
        self.board[y, x] = color
        
        # Check for captures
        opponent = WHITE if color == BLACK else BLACK
        captured = []
        
        # Check adjacent groups for captures
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny, nx] == opponent:
                group = self.find_group(nx, ny)
                if not self.has_liberties(group):
                    captured.extend(group)
        
        # Remove captured stones
        for cx, cy in captured:
            self.board[cy, cx] = EMPTY
        
        # Check if the placed stone's group has liberties
        group = self.find_group(x, y)
        if not self.has_liberties(group):
            # If no liberties and no captures, this is a suicide move
            if not captured:
                # Revert the board state
                self.board = self.last_board_state
                return False
        
        # Check for ko rule violation
        if self.is_ko():
            # Revert the board state
            self.board = self.last_board_state
            return False
        
        return True
    
    def find_group(self, x, y):
        """
        Find all stones in the same group as the stone at (x, y).
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        
        Returns:
            list: List of (x, y) coordinates in the group
        """
        color = self.board[y, x]
        if color == EMPTY:
            return []
        
        group = []
        visited = set()
        
        def dfs(cx, cy):
            if (cx, cy) in visited:
                return
            
            visited.add((cx, cy))
            if 0 <= cx < self.size and 0 <= cy < self.size and self.board[cy, cx] == color:
                group.append((cx, cy))
                dfs(cx+1, cy)
                dfs(cx-1, cy)
                dfs(cx, cy+1)
                dfs(cx, cy-1)
        
        dfs(x, y)
        return group
    
    def has_liberties(self, group):
        """
        Check if a group of stones has any liberties.
        
        Args:
            group (list): List of (x, y) coordinates in the group
        
        Returns:
            bool: True if the group has liberties, False otherwise
        """
        for x, y in group:
            for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny, nx] == EMPTY:
                    return True
        return False
    
    def is_ko(self):
        """
        Check if the current move violates the ko rule.
        
        Returns:
            bool: True if the move violates the ko rule, False otherwise
        """
        if self.last_board_state is None:
            return False
        
        # Simple ko rule: the board state cannot be the same as the previous state
        # This is a simplified version of the ko rule
        return np.array_equal(self.board, self.last_board_state)
    
    def get_legal_moves(self, color):
        """
        Get all legal moves for the specified color.
        
        Args:
            color (int): Stone color (BLACK or WHITE)
        
        Returns:
            list: List of (x, y) coordinates for legal moves
        """
        legal_moves = []
        
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y, x] == EMPTY:
                    # Create a copy of the board to test the move
                    board_copy = Board(self.size)
                    board_copy.board = self.board.copy()
                    board_copy.last_board_state = self.last_board_state.copy() if self.last_board_state is not None else None
                    
                    if board_copy.place_stone(x, y, color):
                        legal_moves.append((x, y))
        
        return legal_moves
    
    def clear(self):
        """
        Clear the board.
        """
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.last_board_state = None
