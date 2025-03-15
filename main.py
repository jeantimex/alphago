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
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_MARGIN
)
from game.game_state import GameState

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    board_size_pixels = (BOARD_SIZE - 1) * CELL_SIZE  # Actual board size in pixels
    # Add extra window space for UI elements and padding
    window_width = board_size_pixels + 2 * BOARD_PADDING + 100  # Extra space for UI
    window_height = board_size_pixels + 2 * BOARD_PADDING + 150  # Extra space for UI and territory controls
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
    show_territory = False
    show_influence = False
    
    # Create button for territory visualization
    territory_button = pygame.Rect(
        window_width // 2 - BUTTON_WIDTH - BUTTON_MARGIN,
        window_height - BUTTON_HEIGHT - BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    
    # Create button for influence visualization
    influence_button = pygame.Rect(
        window_width // 2 + BUTTON_MARGIN,
        window_height - BUTTON_HEIGHT - BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
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
                    
                    # Check if territory button was clicked
                    if territory_button.collidepoint(mouse_pos):
                        show_territory = not show_territory
                        if show_territory:
                            show_influence = False  # Turn off influence when showing territory
                    
                    # Check if influence button was clicked
                    elif influence_button.collidepoint(mouse_pos):
                        show_influence = not show_influence
                        if show_influence:
                            show_territory = False  # Turn off territory when showing influence
                    
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
                elif event.key == pygame.K_t:
                    # Toggle territory visualization
                    show_territory = not show_territory
                    if show_territory:
                        show_influence = False
                elif event.key == pygame.K_i:
                    # Toggle influence visualization
                    show_influence = not show_influence
                    if show_influence:
                        show_territory = False
        
        # Update game timer
        game_time = int(time.time() - start_time)
        minutes = game_time // 60
        seconds = game_time % 60
        
        # Draw the board
        screen.fill((240, 217, 181))  # Wooden background color
        
        # Get territory and influence data if needed
        territory_data = None
        if show_territory or show_influence:
            territory_data = game_state.get_potential_territory()
        
        # Draw territory or influence if enabled
        if show_territory and territory_data:
            potential_territory_map = territory_data['potential_territory_map']
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    territory_type = potential_territory_map[y, x]
                    if territory_type == BLACK_TERRITORY:
                        # Create a surface with per-pixel alpha
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        s.fill(BLACK_TERRITORY_COLOR)
                        screen.blit(s, (board_x_offset + x * CELL_SIZE - CELL_SIZE//2, 
                                       board_y_offset + y * CELL_SIZE - CELL_SIZE//2))
                    elif territory_type == WHITE_TERRITORY:
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        s.fill(WHITE_TERRITORY_COLOR)
                        screen.blit(s, (board_x_offset + x * CELL_SIZE - CELL_SIZE//2, 
                                       board_y_offset + y * CELL_SIZE - CELL_SIZE//2))
                    elif territory_type == POTENTIAL_BLACK_TERRITORY:
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        s.fill(POTENTIAL_BLACK_TERRITORY_COLOR)
                        screen.blit(s, (board_x_offset + x * CELL_SIZE - CELL_SIZE//2, 
                                       board_y_offset + y * CELL_SIZE - CELL_SIZE//2))
                    elif territory_type == POTENTIAL_WHITE_TERRITORY:
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        s.fill(POTENTIAL_WHITE_TERRITORY_COLOR)
                        screen.blit(s, (board_x_offset + x * CELL_SIZE - CELL_SIZE//2, 
                                       board_y_offset + y * CELL_SIZE - CELL_SIZE//2))
        
        # Draw influence if enabled
        if show_influence and territory_data:
            influence_map = territory_data['influence']
            max_influence = max(1.0, np.max(np.abs(influence_map)))  # Normalize influence
            
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if board.get_stone(x, y) == EMPTY:
                        influence_value = influence_map[y, x]
                        if influence_value > 0:  # Black influence
                            intensity = min(255, int(255 * (influence_value / max_influence)))
                            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                            s.fill((0, 0, 0, intensity))
                            screen.blit(s, (board_x_offset + x * CELL_SIZE - CELL_SIZE//2, 
                                           board_y_offset + y * CELL_SIZE - CELL_SIZE//2))
                        elif influence_value < 0:  # White influence
                            intensity = min(255, int(255 * (-influence_value / max_influence)))
                            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                            s.fill((255, 255, 255, intensity))
                            screen.blit(s, (board_x_offset + x * CELL_SIZE - CELL_SIZE//2, 
                                           board_y_offset + y * CELL_SIZE - CELL_SIZE//2))
        
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
                if stone != 0:
                    color = (0, 0, 0) if stone == BLACK else (255, 255, 255)
                    pygame.draw.circle(
                        screen, 
                        color, 
                        (board_x_offset + x * CELL_SIZE, board_y_offset + y * CELL_SIZE), 
                        CELL_SIZE // 2 - 1
                    )
        
        # Display current player with stone icon
        font = pygame.font.SysFont('Arial', 20)
        player_text = "Current Player: "
        text_surface = font.render(player_text, True, (0, 0, 0))
        text_width = text_surface.get_width()
        
        # Center the player indicator
        player_indicator_x = window_width // 2 - text_width // 2 - 15  # Adjust for stone icon
        screen.blit(text_surface, (player_indicator_x, 20))
        
        # Draw current player stone icon
        stone_color = (0, 0, 0) if game_state.current_player == BLACK else (255, 255, 255)
        pygame.draw.circle(
            screen,
            stone_color,
            (player_indicator_x + text_width + 15, 30),  # Position after text
            15  # Larger stone for visibility
        )
        
        # Display timer in top right corner
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        timer_surface = font.render(timer_text, True, (0, 0, 0))
        screen.blit(timer_surface, (window_width - timer_surface.get_width() - 20, 20))
        
        # Display territory score if territory is shown
        if show_territory and territory_data:
            black_score = territory_data[BLACK]
            white_score = territory_data[WHITE]
            score_text = f"Territory - Black: {black_score} | White: {white_score}"
            score_surface = font.render(score_text, True, (0, 0, 0))
            screen.blit(score_surface, (window_width // 2 - score_surface.get_width() // 2, 50))
        
        # Draw territory button
        pygame.draw.rect(screen, (200, 200, 200), territory_button)
        pygame.draw.rect(screen, (0, 0, 0), territory_button, 2)
        territory_text = font.render("Show Territory", True, (0, 0, 0))
        screen.blit(territory_text, (territory_button.x + (territory_button.width - territory_text.get_width()) // 2, 
                                    territory_button.y + (territory_button.height - territory_text.get_height()) // 2))
        
        # Draw influence button
        pygame.draw.rect(screen, (200, 200, 200), influence_button)
        pygame.draw.rect(screen, (0, 0, 0), influence_button, 2)
        influence_text = font.render("Show Influence", True, (0, 0, 0))
        screen.blit(influence_text, (influence_button.x + (influence_button.width - influence_text.get_width()) // 2, 
                                    influence_button.y + (influence_button.height - influence_text.get_height()) // 2))
        
        # Highlight active button
        if show_territory:
            pygame.draw.rect(screen, (100, 200, 100), territory_button, 3)
        if show_influence:
            pygame.draw.rect(screen, (100, 200, 100), influence_button, 3)
        
        # Update the display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
