#!/usr/bin/env python3
"""
AlphaGo Implementation - Main Game File
A PyGame-based implementation of the Go board game with basic game mechanics.
"""

import pygame
import sys
import time
import numpy as np
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
    if show_influence:
        pygame.draw.rect(screen, (100, 100, 200), button)  # Highlighted when active
    else:
        pygame.draw.rect(screen, (200, 200, 200), button)  # Gray when inactive
    
    pygame.draw.rect(screen, (0, 0, 0), button, 2)  # Black border
    
    # Draw button text
    font = pygame.font.Font(None, 24)
    text = font.render("Statistics", True, (0, 0, 0))
    text_rect = text.get_rect(center=button.center)
    screen.blit(text, text_rect)

def draw_move_numbers_button(screen, button, show_move_numbers):
    """Draw the move numbers button with appropriate colors based on state"""
    if show_move_numbers:
        pygame.draw.rect(screen, (100, 200, 100), button)  # Highlighted when active
    else:
        pygame.draw.rect(screen, (200, 200, 200), button)  # Gray when inactive
    
    pygame.draw.rect(screen, (0, 0, 0), button, 2)  # Black border
    
    # Draw button text
    font = pygame.font.Font(None, 24)
    text = font.render("Move Numbers", True, (0, 0, 0))
    text_rect = text.get_rect(center=button.center)
    screen.blit(text, text_rect)

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
    
    # Game timer variables
    start_time = time.time()
    game_time = 0
    
    # Territory visualization flags
    show_territory = False  # Don't show territory by default
    show_influence = False  # Don't show influence by default
    show_move_numbers = False  # Don't show move numbers by default
    territory_size = 0.6  # Fixed size for territory markers
    
    # Define colors
    BLACK_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)
    BOARD_COLOR = (219, 179, 107)  # Tan color for the board
    STONE_RADIUS = CELL_SIZE // 2 - 1
    
    # Create button for influence visualization
    statistics_button = pygame.Rect(
        window_width - 180,
        window_height - 60,
        120,
        40
    )
    
    # Create button for move numbers
    move_numbers_button = pygame.Rect(
        window_width - 350,
        window_height - 60,
        160,
        40
    )
    
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
                    
                    # Check if move numbers button was clicked
                    elif move_numbers_button.collidepoint(mouse_pos):
                        show_move_numbers = not show_move_numbers
                    
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
                            else:
                                print(f"Invalid move at ({board_x}, {board_y})")
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Pass turn
                    game_state.pass_turn()
                    print(f"{game_state.current_player_name()} passed")
                elif event.key == pygame.K_r:
                    # Reset game
                    board = Board(BOARD_SIZE)
                    game_state = GameState(board)
                    start_time = time.time()  # Reset timer
                    print("Game reset")
                elif event.key == pygame.K_i:
                    # Toggle influence visualization
                    show_influence = not show_influence
                    # Don't toggle territory when toggling influence
        
        # Update game timer
        game_time = int(time.time() - start_time)
        minutes = game_time // 60
        seconds = game_time % 60
        
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
        
        # Display timer in top right corner
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        timer_surface = font.render(timer_text, True, BLACK_COLOR)
        screen.blit(timer_surface, (window_width - timer_surface.get_width() - 20, 20))
        
        # Draw buttons
        draw_statistics_button(screen, statistics_button, show_influence)
        draw_move_numbers_button(screen, move_numbers_button, show_move_numbers)
        
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
