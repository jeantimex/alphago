#!/usr/bin/env python3
"""
AlphaGo Implementation - Main Game File
A PyGame-based implementation of the Go board game with basic game mechanics.
"""

import pygame
import sys
import numpy as np
import os
from game.board import Board
from game.constants import (
    BLACK, WHITE, EMPTY, BOARD_SIZE, CELL_SIZE, BOARD_PADDING,
    BLACK_TERRITORY, WHITE_TERRITORY, POTENTIAL_BLACK_TERRITORY, POTENTIAL_WHITE_TERRITORY,
    BLACK_TERRITORY_COLOR, WHITE_TERRITORY_COLOR, 
    POTENTIAL_BLACK_TERRITORY_COLOR, POTENTIAL_WHITE_TERRITORY_COLOR,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_MARGIN,
    TERRITORY_MARKER_SHAPE
)
from game.game_state import GameState
from game.sgf_parser import SGFParser

def draw_territory_marker(screen, x, y, size, color):
    """
    Draw a territory marker at the specified position.
    
    Args:
        screen: Pygame screen to draw on
        x, y: Position to draw the marker
        size: Size of the marker
        color: Color of the marker (RGBA)
    """
    if TERRITORY_MARKER_SHAPE == "circle":
        # Create a surface with per-pixel alpha
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (size // 2, size // 2), size // 2)
        screen.blit(s, (x - size // 2, y - size // 2))
    elif TERRITORY_MARKER_SHAPE == "square":
        # Create a surface with per-pixel alpha
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, size, size))
        screen.blit(s, (x - size // 2, y - size // 2))
    elif TERRITORY_MARKER_SHAPE == "diamond":
        # Create a surface with per-pixel alpha
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        points = [
            (size // 2, 0),
            (size, size // 2),
            (size // 2, size),
            (0, size // 2)
        ]
        pygame.draw.polygon(s, color, points)
        screen.blit(s, (x - size // 2, y - size // 2))

def draw_statistics_button(screen, button, show_influence):
    """Draw the statistics button with appropriate colors based on state"""
    color = (180, 180, 220) if show_influence else (200, 200, 200)
    pygame.draw.rect(screen, color, button)
    font = pygame.font.Font(None, 24)
    text = font.render("Statistics", True, (0, 0, 0))
    screen.blit(text, (button.centerx - text.get_width() // 2, button.centery - text.get_height() // 2))

def draw_load_game_button(screen, button):
    """Draw the load game button"""
    pygame.draw.rect(screen, (200, 200, 200), button)
    font = pygame.font.Font(None, 24)
    text = font.render("Load Game", True, (0, 0, 0))
    screen.blit(text, (button.centerx - text.get_width() // 2, button.centery - text.get_height() // 2))

def draw_move_numbers_button(screen, button, show_move_numbers):
    """Draw the move numbers button with appropriate colors based on state"""
    color = (180, 180, 220) if show_move_numbers else (200, 200, 200)
    pygame.draw.rect(screen, color, button)
    font = pygame.font.Font(None, 24)
    text = font.render("Move Numbers", True, (0, 0, 0))
    screen.blit(text, (button.centerx - text.get_width() // 2, button.centery - text.get_height() // 2))

def draw_navigation_button(screen, button, text, enabled):
    """Draw a navigation button (previous/next) with appropriate colors based on state"""
    color = (200, 200, 200) if enabled else (150, 150, 150)
    pygame.draw.rect(screen, color, button)
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, (0, 0, 0) if enabled else (100, 100, 100))
    screen.blit(text_surface, (button.centerx - text_surface.get_width() // 2, button.centery - text_surface.get_height() // 2))
    
    # Draw a border around the button
    pygame.draw.rect(screen, (0, 0, 0), button, 2)

class SimpleFileDialog:
    """A simple file dialog implementation using pygame"""
    
    def __init__(self, screen, title, start_dir, filter_ext=None):
        self.screen = screen
        self.title = title
        self.current_dir = start_dir
        self.filter_ext = filter_ext
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.files = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_items = 15
        self.load_files()
        
        # Dialog dimensions
        self.width = 600
        self.height = 500
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Buttons
        button_width = 100
        button_height = 40
        button_margin = 20
        self.cancel_button = pygame.Rect(
            self.x + self.width - button_width - button_margin,
            self.y + self.height - button_height - button_margin,
            button_width,
            button_height
        )
        self.select_button = pygame.Rect(
            self.x + self.width - 2 * button_width - 2 * button_margin,
            self.y + self.height - button_height - button_margin,
            button_width,
            button_height
        )
    
    def load_files(self):
        """Load files and directories from the current directory"""
        self.files = []
        
        # Add parent directory option
        self.files.append(("..", True))
        
        try:
            # List all files and directories
            for item in os.listdir(self.current_dir):
                full_path = os.path.join(self.current_dir, item)
                is_dir = os.path.isdir(full_path)
                
                # Filter files by extension if specified
                if not is_dir and self.filter_ext and not item.lower().endswith(self.filter_ext.lower()):
                    continue
                
                self.files.append((item, is_dir))
            
            # Sort directories first, then files
            self.files.sort(key=lambda x: (not x[1], x[0].lower()))
        except Exception as e:
            print(f"Error loading files: {e}")
    
    def handle_event(self, event):
        """Handle pygame events for the file dialog"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                # Adjust scroll if needed
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.files) - 1, self.selected_index + 1)
                # Adjust scroll if needed
                if self.selected_index >= self.scroll_offset + self.max_items:
                    self.scroll_offset = self.selected_index - self.max_items + 1
            elif event.key == pygame.K_RETURN:
                # Handle selection
                if self.selected_index < len(self.files):
                    item, is_dir = self.files[self.selected_index]
                    
                    if is_dir:
                        # Navigate to directory
                        if item == "..":
                            self.current_dir = os.path.dirname(self.current_dir)
                        else:
                            self.current_dir = os.path.join(self.current_dir, item)
                        self.load_files()
                        return None
                    else:
                        # Return the selected file path
                        return os.path.join(self.current_dir, item)
            elif event.key == pygame.K_ESCAPE:
                # Cancel selection
                return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Calculate which item was clicked
                mouse_y = event.pos[1]
                item_height = 30
                header_height = 60
                
                # Check if click is in the file list area
                if mouse_y > header_height:
                    clicked_index = self.scroll_offset + (mouse_y - header_height) // item_height
                    
                    if 0 <= clicked_index < len(self.files):
                        if clicked_index == self.selected_index:
                            # Double-click handling (simplified)
                            item, is_dir = self.files[self.selected_index]
                            
                            if is_dir:
                                # Navigate to directory
                                if item == "..":
                                    self.current_dir = os.path.dirname(self.current_dir)
                                else:
                                    self.current_dir = os.path.join(self.current_dir, item)
                                self.load_files()
                                return None
                            else:
                                # Return the selected file path
                                return os.path.join(self.current_dir, item)
                        else:
                            # Single click - update selection
                            self.selected_index = clicked_index
            
            elif event.button == 4:  # Mouse wheel up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Mouse wheel down
                self.scroll_offset = min(
                    max(0, len(self.files) - self.max_items),
                    self.scroll_offset + 1
                )
        
        return None
    
    def draw(self):
        """Draw the file dialog"""
        # Draw background
        self.screen.fill((240, 240, 240))
        
        # Draw title
        title_surf = self.title_font.render(self.title, True, (0, 0, 0))
        self.screen.blit(title_surf, (20, 10))
        
        # Draw current directory
        dir_surf = self.font.render(f"Directory: {self.current_dir}", True, (0, 0, 0))
        self.screen.blit(dir_surf, (20, 40))
        
        # Draw separator line
        pygame.draw.line(self.screen, (100, 100, 100), (0, 60), (self.screen.get_width(), 60), 2)
        
        # Draw file list
        item_height = 30
        visible_range = range(
            self.scroll_offset,
            min(len(self.files), self.scroll_offset + self.max_items)
        )
        
        for i, idx in enumerate(visible_range):
            item, is_dir = self.files[idx]
            y_pos = 60 + i * item_height
            
            # Highlight selected item
            if idx == self.selected_index:
                pygame.draw.rect(
                    self.screen,
                    (200, 200, 255),
                    (0, y_pos, self.screen.get_width(), item_height)
                )
            
            # Draw item text
            if is_dir:
                item_text = f"📁 {item}"
            else:
                item_text = f"📄 {item}"
            
            text_surf = self.font.render(item_text, True, (0, 0, 0))
            self.screen.blit(text_surf, (20, y_pos + 5))
        
        # Draw scrollbar if needed
        if len(self.files) > self.max_items:
            scrollbar_height = self.screen.get_height() - 60
            thumb_size = scrollbar_height * min(1.0, self.max_items / len(self.files))
            thumb_pos = 60 + (scrollbar_height - thumb_size) * (self.scroll_offset / max(1, len(self.files) - self.max_items))
            
            # Draw scrollbar background
            pygame.draw.rect(
                self.screen,
                (220, 220, 220),
                (self.screen.get_width() - 20, 60, 20, scrollbar_height)
            )
            
            # Draw scrollbar thumb
            pygame.draw.rect(
                self.screen,
                (180, 180, 180),
                (self.screen.get_width() - 20, thumb_pos, 20, thumb_size)
            )
        
        # Draw instructions
        instructions = "Use arrow keys to navigate, Enter to select, Escape to cancel"
        instr_surf = self.font.render(instructions, True, (0, 0, 0))
        self.screen.blit(
            instr_surf,
            (20, self.screen.get_height() - 30)
        )
        
        # Draw buttons
        pygame.draw.rect(self.screen, (200, 200, 200), self.cancel_button)
        pygame.draw.rect(self.screen, (200, 200, 200), self.select_button)
        font = pygame.font.Font(None, 24)
        cancel_text = font.render("Cancel", True, (0, 0, 0))
        select_text = font.render("Select", True, (0, 0, 0))
        self.screen.blit(cancel_text, (self.cancel_button.centerx - cancel_text.get_width() // 2, self.cancel_button.centery - cancel_text.get_height() // 2))
        self.screen.blit(select_text, (self.select_button.centerx - select_text.get_width() // 2, self.select_button.centery - select_text.get_height() // 2))
        
        pygame.display.flip()

    def show(self):
        """
        Show the file dialog and return the selected file path.
        Returns:
            str or None: The selected file path, or None if canceled
        """
        running = True
        selected_file = None
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    selected_file = None
                
                result = self.handle_event(event)
                if result is not None:
                    running = False
                    selected_file = result
            
            self.draw()
            pygame.time.delay(10)  # Small delay to reduce CPU usage
        
        return selected_file

def load_sgf_file(screen):
    """Show a file dialog to select an SGF file"""
    # Save the current screen state
    old_screen = screen.copy()
    
    # Create a new screen for the dialog
    dialog_screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Select SGF File")
    
    # Create and run the file dialog
    file_dialog = SimpleFileDialog(dialog_screen, title="Select SGF File", start_dir=os.getcwd(), filter_ext=".sgf")
    
    running = True
    selected_file = None
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                selected_file = False  # Cancel
            
            result = file_dialog.handle_event(event)
            if result is not None:
                running = False
                selected_file = result
        
        file_dialog.draw()
    
    # Restore the original screen
    screen = pygame.display.set_mode((screen.get_width(), screen.get_height()))
    screen.blit(old_screen, (0, 0))
    pygame.display.flip()
    
    return selected_file

def load_game_from_sgf(file_path, board, game_state):
    """
    Load a game from an SGF file
    
    Args:
        file_path (str): Path to the SGF file
        board (Board): The game board to update
        game_state (GameState): The game state to update
        
    Returns:
        bool: True if the game was loaded successfully, False otherwise
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Invalid SGF file path: {file_path}")
        return False
    
    # Parse the SGF file
    parser = SGFParser()
    game_data = parser.parse_file(file_path)
    
    if not game_data:
        print("Failed to parse SGF file")
        return False
    
    # Reset the board and game state
    board.clear()
    game_state = GameState(board)
    
    # Get game information
    game_info = parser.get_game_info()
    print(f"Loaded game: {os.path.basename(file_path)}")
    print(f"Black: {game_info['black_player']}, White: {game_info['white_player']}")
    print(f"Date: {game_info['date']}, Result: {game_info['result']}")
    
    # Apply all moves from the SGF file
    for move in game_info['moves']:
        color, x, y = move
        
        # Handle passes
        if x is None or y is None:
            game_state.pass_turn()
            continue
        
        # Set the current player
        if color == 'B':
            game_state.current_player = BLACK
        else:
            game_state.current_player = WHITE
        
        # Place the stone
        if not game_state.place_stone(x, y):
            print(f"Warning: Invalid move in SGF file: {color} at ({x}, {y})")
    
    # Set the current player to the next player after the last move
    if game_info['moves'] and game_info['moves'][-1][0] == 'B':
        game_state.current_player = WHITE
    else:
        game_state.current_player = BLACK
    
    return True

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 800
    board_size_pixels = (BOARD_SIZE - 1) * CELL_SIZE  # Actual board size in pixels
    # Add extra window space for UI elements and padding
    window_width = board_size_pixels + 2 * BOARD_PADDING + 100  # Extra space for UI
    window_height = board_size_pixels + 2 * BOARD_PADDING + 250  # Extra space for UI and territory controls
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("AlphaGo Implementation")
    
    # Calculate board position to center it
    board_x_offset = (window_width - board_size_pixels) // 2
    board_y_offset = (window_height - board_size_pixels) // 2 - 25  # Shift up to make room for territory controls
    
    # Create game objects
    board = Board(BOARD_SIZE)
    game_state = GameState(board)
    
    # Game state navigation variables
    current_move_index = 0
    # Store the initial empty board state
    game_states = [(board.copy(), [])]
    
    # Territory visualization flags
    show_territory = False  # Don't show territory by default
    show_influence = False  # Don't show influence by default
    show_move_numbers = False  # Don't show move numbers by default
    territory_size = 0.6  # Fixed size for territory markers
    
    # Create button for influence visualization
    statistics_button = pygame.Rect(
        window_width - 180,
        window_height - 60,
        120,
        40
    )
    
    # Create button for load game
    load_game_button = pygame.Rect(
        window_width - 320,
        window_height - 60,
        120,
        40
    )
    
    # Create button for move numbers
    move_numbers_button = pygame.Rect(
        window_width - 460,
        window_height - 60,
        120,
        40
    )
    
    # Create navigation buttons (previous and next)
    nav_button_width = 60
    nav_button_height = 40
    nav_button_y = window_height - 120  # Position above the other buttons
    
    # Center the navigation buttons horizontally
    nav_buttons_total_width = 2 * nav_button_width + 20  # 20px spacing between buttons
    nav_buttons_start_x = (window_width - nav_buttons_total_width) // 2
    
    previous_button = pygame.Rect(
        nav_buttons_start_x,
        nav_button_y,
        nav_button_width,
        nav_button_height
    )
    
    next_button = pygame.Rect(
        nav_buttons_start_x + nav_button_width + 20,  # 20px spacing
        nav_button_y,
        nav_button_width,
        nav_button_height
    )
    
    # Define colors
    BLACK_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)
    BOARD_COLOR = (219, 179, 107)  # Tan color for the board
    STONE_RADIUS = CELL_SIZE // 2 - 1
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = event.pos
                    
                    # Check if statistics button was clicked
                    if statistics_button.collidepoint(mouse_pos):
                        show_influence = not show_influence
                        # No need to toggle territory since we don't show it anymore
                    
                    # Check if load game button was clicked
                    elif load_game_button.collidepoint(mouse_pos):
                        print("Load game button clicked")
                        # Create and show file dialog
                        file_dialog = SimpleFileDialog(screen, "Load SGF File", os.getcwd(), filter_ext=".sgf")
                        sgf_file = file_dialog.show()
                        
                        if sgf_file:
                            print(f"Loading game from {sgf_file}")
                            # Parse SGF file
                            parser = SGFParser()
                            game_info = parser.parse_file(sgf_file)
                            
                            if game_info and 'moves' in game_info:
                                print(f"Successfully parsed SGF with {len(game_info['moves'])} moves")
                                
                                # Reset the game
                                board = Board(BOARD_SIZE)
                                game_state = GameState(board)
                                
                                # Reset game states for navigation
                                game_states = [(board.copy(), [])]
                                current_move_index = 0
                                
                                # Apply moves from SGF
                                for move in game_info['moves']:
                                    x, y, color = move
                                    if x is not None and y is not None:  # Skip pass moves
                                        # Set the current player to match the SGF move color
                                        game_state.current_player = color
                                        
                                        # Place the stone
                                        if game_state.place_stone(x, y):
                                            # Add the new board state and move history to game_states
                                            game_states.append((board.copy(), game_state.move_history[:]))
                                            current_move_index = len(game_states) - 1
                                
                                print(f"Game loaded with {len(game_info['moves'])} moves")
                                print(f"Created {len(game_states)} game states for navigation")
                                
                                # Debug the game states
                                for i, (b, m) in enumerate(game_states):
                                    print(f"  State {i}: Board has {np.count_nonzero(b.board)} stones, {len(m)} moves in history")
                            else:
                                print("Failed to parse SGF file or no moves found")
                    
                    # Check if move numbers button was clicked
                    elif move_numbers_button.collidepoint(mouse_pos):
                        show_move_numbers = not show_move_numbers
                    
                    # Check if previous button was clicked
                    elif previous_button.collidepoint(mouse_pos) and current_move_index > 0:
                        current_move_index -= 1
                        print(f"Moving to previous state {current_move_index} of {len(game_states)-1}")
                        
                        # Restore previous board state
                        prev_board, prev_history = game_states[current_move_index]
                        # We need to copy the board's internal state
                        board.board = prev_board.board.copy()
                        board.last_board_state = prev_board.last_board_state.copy() if prev_board.last_board_state is not None else None
                        board.previous_board_states = [s.copy() if isinstance(s, np.ndarray) else s for s in prev_board.previous_board_states]
                        board.ko_position = prev_board.ko_position
                        
                        # Update game state
                        game_state.move_history = prev_history[:]
                        
                        # Set current player based on the last move
                        if prev_history:
                            last_player = prev_history[-1][2]
                            game_state.current_player = WHITE if last_player == BLACK else BLACK
                        else:
                            game_state.current_player = BLACK  # Default to BLACK for first move
                        
                        print(f"Moved to previous state (move {current_move_index})")
                    
                    # Check if next button was clicked
                    elif next_button.collidepoint(mouse_pos) and current_move_index < len(game_states) - 1:
                        current_move_index += 1
                        print(f"Moving to next state {current_move_index} of {len(game_states)-1}")
                        
                        # Restore next board state
                        next_board, next_history = game_states[current_move_index]
                        # We need to copy the board's internal state
                        board.board = next_board.board.copy()
                        board.last_board_state = next_board.last_board_state.copy() if next_board.last_board_state is not None else None
                        board.previous_board_states = [s.copy() if isinstance(s, np.ndarray) else s for s in next_board.previous_board_states]
                        board.ko_position = next_board.ko_position
                        
                        # Update game state
                        game_state.move_history = next_history[:]
                        
                        # Set current player based on the last move
                        if next_history:
                            last_player = next_history[-1][2]
                            game_state.current_player = WHITE if last_player == BLACK else BLACK
                        else:
                            game_state.current_player = BLACK  # Default to BLACK for first move
                        
                        print(f"Moved to next state (move {current_move_index})")
                    
                    else:
                        # Get board coordinates from mouse position
                        x, y = event.pos
                        board_x = round((x - board_x_offset) / CELL_SIZE)
                        board_y = round((y - board_y_offset) / CELL_SIZE)
                        
                        # Check if the coordinates are valid
                        if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
                            # Try to place a stone
                            if game_state.place_stone(board_x, board_y):
                                print(f"Stone placed at ({board_x}, {board_y})")
                                
                                # If we're not at the end of the game states list,
                                # truncate the list to the current position
                                if current_move_index < len(game_states) - 1:
                                    print(f"Truncating future states. Before: {len(game_states)}, Current index: {current_move_index}")
                                    game_states = game_states[:current_move_index + 1]
                                    print(f"After truncation: {len(game_states)} states")
                                
                                # Add the new board state and move history
                                new_board_copy = board.copy()
                                new_move_history = game_state.move_history[:]
                                game_states.append((new_board_copy, new_move_history))
                                current_move_index = len(game_states) - 1
                                print(f"Added new game state. Total states: {len(game_states)}, Current index: {current_move_index}")
                                
                                # Debug the game states
                                for i, (b, m) in enumerate(game_states):
                                    print(f"  State {i}: Board has {np.count_nonzero(b.board)} stones, {len(m)} moves in history")
                            else:
                                print(f"Invalid move at ({board_x}, {board_y})")
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Pass turn
                    print("Pass")
                    game_state.pass_turn()
                    print(f"{game_state.current_player_name()} passed")
                    
                    # If we're not at the end of the game states list,
                    # truncate the list to the current position
                    if current_move_index < len(game_states) - 1:
                        game_states = game_states[:current_move_index + 1]
                    
                    # Add the new board state and move history
                    game_states.append((board.copy(), game_state.move_history[:]))
                    current_move_index = len(game_states) - 1
                elif event.key == pygame.K_r:
                    # Reset game
                    board = Board(BOARD_SIZE)
                    game_state = GameState(board)
                    # Reset game state navigation
                    game_states = [(board.copy(), [])]
                    current_move_index = 0
                    print("Game reset")
                elif event.key == pygame.K_i:
                    # Toggle influence visualization
                    show_influence = not show_influence
                    # Don't toggle territory when toggling influence
                elif event.key == pygame.K_LEFT:
                    # Previous move
                    if current_move_index > 0:
                        current_move_index -= 1
                        print(f"Moving to previous state {current_move_index} of {len(game_states)-1}")
                        
                        # Restore previous board state
                        prev_board, prev_history = game_states[current_move_index]
                        # We need to copy the board's internal state
                        board.board = prev_board.board.copy()
                        board.last_board_state = prev_board.last_board_state.copy() if prev_board.last_board_state is not None else None
                        board.previous_board_states = [s.copy() if isinstance(s, np.ndarray) else s for s in prev_board.previous_board_states]
                        board.ko_position = prev_board.ko_position
                        
                        # Update game state
                        game_state.move_history = prev_history[:]
                        
                        # Set current player based on the last move
                        if prev_history:
                            last_player = prev_history[-1][2]
                            game_state.current_player = WHITE if last_player == BLACK else BLACK
                        else:
                            game_state.current_player = BLACK  # Default to BLACK for first move
                        
                        print(f"Moved to previous state (move {current_move_index})")
                elif event.key == pygame.K_RIGHT:
                    # Next move
                    if current_move_index < len(game_states) - 1:
                        current_move_index += 1
                        print(f"Moving to next state {current_move_index} of {len(game_states)-1}")
                        
                        # Restore next board state
                        next_board, next_history = game_states[current_move_index]
                        # We need to copy the board's internal state
                        board.board = next_board.board.copy()
                        board.last_board_state = next_board.last_board_state.copy() if next_board.last_board_state is not None else None
                        board.previous_board_states = [s.copy() if isinstance(s, np.ndarray) else s for s in next_board.previous_board_states]
                        board.ko_position = next_board.ko_position
                        
                        # Update game state
                        game_state.move_history = next_history[:]
                        
                        # Set current player based on the last move
                        if next_history:
                            last_player = next_history[-1][2]
                            game_state.current_player = WHITE if last_player == BLACK else BLACK
                        else:
                            game_state.current_player = BLACK  # Default to BLACK for first move
                        
                        print(f"Moved to next state (move {current_move_index})")
        
        # Draw the board
        screen.fill(BOARD_COLOR)  # Wooden background color
        
        # Get territory and influence data if needed
        territory_data = None
        potential_territory_map = None
        influence_map = None
        black_influence_total = 0
        white_influence_total = 0
        
        if show_influence:
            # Calculate influence map
            territory_data = game_state.get_potential_territory()
            influence_map = territory_data['influence']
            max_influence = max(1.0, np.max(np.abs(influence_map)))  # Normalize influence
            
            # Calculate total influence for each player
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    influence_value = influence_map[y, x]
                    if influence_value > 0:  # Black influence
                        black_influence_total += influence_value
                    elif influence_value < 0:  # White influence (negative values)
                        white_influence_total -= influence_value  # Convert to positive
            
            # Draw influence
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if board.get_stone(x, y) == EMPTY:
                        influence_value = influence_map[y, x]
                        
                        # Skip very small influence values
                        if abs(influence_value) < 0.1:
                            continue
                        
                        # Calculate position
                        pos_x = board_x_offset + x * CELL_SIZE
                        pos_y = board_y_offset + y * CELL_SIZE
                        
                        # Calculate rectangle size based on influence value
                        # Apply a scaling factor to make rectangles bigger overall
                        base_size_factor = 0.3  # Minimum size factor (for very small influence)
                        max_size_factor = 0.9   # Maximum size factor (for maximum influence)
                        
                        # Scale the influence value to a size between base_size_factor and max_size_factor
                        size_factor = base_size_factor + (max_size_factor - base_size_factor) * min(1.0, abs(influence_value) / max_influence)
                        
                        # Calculate the actual pixel size
                        rect_size = int(CELL_SIZE * size_factor)
                        
                        # Ensure minimum size for visibility
                        rect_size = max(rect_size, 8)
                        
                        # Create rectangle centered on the point
                        rect = pygame.Rect(
                            pos_x - rect_size // 2,
                            pos_y - rect_size // 2,
                            rect_size,
                            rect_size
                        )
                        
                        # Color based on which player has influence (black or white)
                        if influence_value > 0:  # Black influence
                            # Create a black color with transparency based on influence value
                            alpha = int(min(255, 100 + 155 * (abs(influence_value) / max_influence)))
                            # Create a surface with per-pixel alpha
                            s = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
                            s.fill((0, 0, 0, alpha))  # Black with transparency
                            screen.blit(s, (pos_x - rect_size // 2, pos_y - rect_size // 2))
                        elif influence_value < 0:  # White influence
                            # Create a white color with transparency based on influence value
                            alpha = int(min(255, 100 + 155 * (abs(influence_value) / max_influence)))
                            # Create a surface with per-pixel alpha
                            s = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
                            s.fill((255, 255, 255, alpha))  # White with transparency
                            screen.blit(s, (pos_x - rect_size // 2, pos_y - rect_size // 2))
        
        # Draw grid lines
        for i in range(BOARD_SIZE):
            # Vertical lines
            pygame.draw.line(
                screen, 
                (0, 0, 0), 
                (board_x_offset + i * CELL_SIZE, board_y_offset), 
                (board_x_offset + i * CELL_SIZE, board_y_offset + (BOARD_SIZE - 1) * CELL_SIZE),
                2 if i == 0 or i == BOARD_SIZE - 1 else 1
            )
            # Horizontal lines
            pygame.draw.line(
                screen, 
                (0, 0, 0), 
                (board_x_offset, board_y_offset + i * CELL_SIZE), 
                (board_x_offset + (BOARD_SIZE - 1) * CELL_SIZE, board_y_offset + i * CELL_SIZE),
                2 if i == 0 or i == BOARD_SIZE - 1 else 1
            )
        
        # Draw star points (hoshi)
        star_points = []
        if BOARD_SIZE == 19:
            star_points = [(3, 3), (9, 3), (15, 3), (3, 9), (9, 9), (15, 9), (3, 15), (9, 15), (15, 15)]
        elif BOARD_SIZE == 13:
            star_points = [(3, 3), (9, 3), (6, 6), (3, 9), (9, 9)]
        elif BOARD_SIZE == 9:
            star_points = [(2, 2), (6, 2), (4, 4), (2, 6), (6, 6)]
        
        for point in star_points:
            x, y = point
            pygame.draw.circle(
                screen, 
                (0, 0, 0), 
                (board_x_offset + x * CELL_SIZE, board_y_offset + y * CELL_SIZE), 
                5
            )
        
        # Draw stones
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                stone = board.get_stone(x, y)
                if stone != EMPTY:
                    # Calculate position
                    pos_x = board_x_offset + x * CELL_SIZE
                    pos_y = board_y_offset + y * CELL_SIZE
                    
                    # Draw stone
                    if stone == BLACK:
                        pygame.draw.circle(screen, BLACK_COLOR, (pos_x, pos_y), STONE_RADIUS)
                    else:
                        pygame.draw.circle(screen, WHITE_COLOR, (pos_x, pos_y), STONE_RADIUS)
                    
                    # Draw move number if enabled
                    if show_move_numbers:
                        # Find the move number for this position
                        move_number = None
                        for i, (move_x, move_y, move_color) in enumerate(game_state.move_history):
                            if move_x == x and move_y == y:
                                move_number = i + 1  # 1-based move numbering
                                break
                        
                        if move_number is not None:
                            # Choose text color based on stone color
                            text_color = WHITE_COLOR if stone == BLACK else BLACK_COLOR
                            
                            # Draw move number
                            font = pygame.font.Font(None, 20)
                            text = font.render(str(move_number), True, text_color)
                            text_rect = text.get_rect(center=(pos_x, pos_y))
                            screen.blit(text, text_rect)
        
        # Display current player with stone icon
        font = pygame.font.SysFont('Arial', 20)
        player_indicator_x = 20
        
        # Display current player text
        text = f"Current Player: "
        text_surface = font.render(text, True, BLACK_COLOR)
        text_width = text_surface.get_width()
        
        # Center the player indicator
        player_indicator_x = 20
        screen.blit(text_surface, (player_indicator_x, 20))
        
        # Draw current player stone icon
        stone_color = BLACK_COLOR if game_state.current_player == BLACK else WHITE_COLOR
        pygame.draw.circle(
            screen,
            stone_color,
            (player_indicator_x + text_width + 15, 20 + text_surface.get_height() // 2),
            10
        )
        
        # Draw buttons
        draw_statistics_button(screen, statistics_button, show_influence)
        draw_load_game_button(screen, load_game_button)
        draw_move_numbers_button(screen, move_numbers_button, show_move_numbers)
        
        # Draw navigation buttons
        has_previous = current_move_index > 0
        has_next = current_move_index < len(game_states) - 1
        print(f"Navigation state: Index={current_move_index}, Total={len(game_states)}, Has Previous={has_previous}, Has Next={has_next}")
        draw_navigation_button(screen, previous_button, "<", has_previous)
        draw_navigation_button(screen, next_button, ">", has_next)
        
        # Display influence scores if statistics is enabled (at the bottom of the board)
        if show_influence and territory_data:
            # Create a larger font for the score display
            score_font = pygame.font.SysFont('Arial', 24)
            
            # Position for the score display at the bottom of the board
            score_y = board_y_offset + board_size_pixels + 30
            
            # Display White's influence with white circle
            white_score_x = WINDOW_WIDTH // 4
            
            # Draw white circle
            pygame.draw.circle(screen, WHITE_COLOR, (white_score_x - 30, score_y), 10)
            pygame.draw.circle(screen, BLACK_COLOR, (white_score_x - 30, score_y), 10, 1)  # Black outline
            
            # Draw white influence text
            white_score_text = f": {white_influence_total:.1f}"
            white_score_surface = score_font.render(white_score_text, True, BLACK_COLOR)
            screen.blit(white_score_surface, (white_score_x - 15, score_y - 12))
            
            # Display Black's influence with black circle
            black_score_x = 3 * WINDOW_WIDTH // 4
            
            # Draw black circle
            pygame.draw.circle(screen, BLACK_COLOR, (black_score_x - 30, score_y), 10)
            
            # Draw black influence text
            black_score_text = f": {black_influence_total:.1f}"
            black_score_surface = score_font.render(black_score_text, True, BLACK_COLOR)
            screen.blit(black_score_surface, (black_score_x - 15, score_y - 12))
            
            # Draw separator
            separator_text = "-"
            separator_surface = score_font.render(separator_text, True, BLACK_COLOR)
            separator_x = WINDOW_WIDTH // 2
            screen.blit(separator_surface, (separator_x - separator_surface.get_width() // 2, score_y - 12))
        
        # Update the display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
