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
from game.constants import BLACK, WHITE, EMPTY, BOARD_SIZE, CELL_SIZE, BOARD_PADDING
from game.game_state import GameState

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    board_size_pixels = (BOARD_SIZE - 1) * CELL_SIZE  # Actual board size in pixels
    # Add extra window space for UI elements and padding
    window_width = board_size_pixels + 2 * BOARD_PADDING + 100  # Extra space for UI
    window_height = board_size_pixels + 2 * BOARD_PADDING + 100  # Extra space for UI
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("AlphaGo Implementation")
    
    # Calculate board position to center it
    board_x_offset = (window_width - board_size_pixels) // 2
    board_y_offset = (window_height - board_size_pixels) // 2
    
    # Create game objects
    board = Board(BOARD_SIZE)
    game_state = GameState(board)
    
    # Game timer variables
    start_time = time.time()
    game_time = 0
    
    # Button dimensions and positions
    button_width = 120
    button_height = 30
    button_padding = 10
    
    # Evaluate button
    evaluate_button_x = 20
    evaluate_button_y = 20
    evaluate_button_rect = pygame.Rect(evaluate_button_x, evaluate_button_y, button_width, button_height)
    
    # Game state variables
    show_territory = False
    show_influence_numbers = False
    potential_territory = True  # Enable potential territory by default
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if evaluate button was clicked
                    if evaluate_button_rect.collidepoint(mouse_pos):
                        show_territory = not show_territory
                        if show_territory:
                            # Calculate territory evaluation
                            game_state.evaluate_territory()
                            print("Territory evaluation displayed")
                        else:
                            show_influence_numbers = False
                            print("Territory evaluation hidden")
                    # Check if numbers button was clicked (only if territory is shown)
                    elif show_territory and numbers_button_rect.collidepoint(mouse_pos):
                        show_influence_numbers = not show_influence_numbers
                        print(f"Influence numbers {'displayed' if show_influence_numbers else 'hidden'}")
                    # Check if potential territory button was clicked (only if territory is shown)
                    elif show_territory and potential_button_rect.collidepoint(mouse_pos):
                        potential_territory = not potential_territory
                        # Update the territory evaluator setting
                        game_state.territory_evaluator.set_potential_territory(potential_territory)
                        # Recalculate territory
                        game_state.evaluate_territory()
                        print(f"Using {'potential' if potential_territory else 'basic'} territory evaluation")
                    else:
                        # Get board coordinates from mouse position
                        x, y = mouse_pos
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
                    show_territory = False
                    show_influence_numbers = False
                    print("Game reset")
                elif event.key == pygame.K_t:
                    # Toggle territory evaluation
                    show_territory = not show_territory
                    if show_territory:
                        game_state.evaluate_territory()
                        print("Territory evaluation displayed")
                    else:
                        show_influence_numbers = False
                        print("Territory evaluation hidden")
                elif event.key == pygame.K_n:
                    # Toggle influence numbers
                    if show_territory:
                        show_influence_numbers = not show_influence_numbers
                        print(f"Influence numbers {'displayed' if show_influence_numbers else 'hidden'}")
                elif event.key == pygame.K_p:
                    # Toggle potential territory
                    if show_territory:
                        potential_territory = not potential_territory
                        # Update the territory evaluator setting
                        game_state.territory_evaluator.set_potential_territory(potential_territory)
                        # Recalculate territory
                        game_state.evaluate_territory()
                        print(f"Using {'potential' if potential_territory else 'basic'} territory evaluation")
        
        # Update game timer
        game_time = int(time.time() - start_time)
        minutes = game_time // 60
        seconds = game_time % 60
        
        # Draw the board
        screen.fill((240, 217, 181))  # Wooden background color
        
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
        
        # Draw territory evaluation if enabled
        if show_territory and game_state.influence_map is not None:
            # Create a surface for territory visualization
            territory_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
            
            # Track which territories are being counted for display
            territory_data = game_state.get_detailed_territory()
            
            # Draw solid rectangles for black territory
            for point, influence in territory_data['black']:
                x, y = point
                # Calculate rectangle size based on influence strength (0.3 to 0.9)
                normalized_influence = 0.3 + (min(abs(influence), 10) / 10) * 0.6
                rect_size = int(CELL_SIZE * normalized_influence)
                
                rect_x = board_x_offset + x * CELL_SIZE - rect_size // 2
                rect_y = board_y_offset + y * CELL_SIZE - rect_size // 2
                pygame.draw.rect(territory_surface, (0, 0, 0, 180), (rect_x, rect_y, rect_size, rect_size))
                
                # Draw a number indicating the influence strength (if enabled)
                if show_influence_numbers:
                    font = pygame.font.SysFont('Arial', 10)
                    text = f"{influence:.1f}"
                    text_surface = font.render(text, True, (255, 0, 0))
                    text_rect = text_surface.get_rect(center=(board_x_offset + x * CELL_SIZE, board_y_offset + y * CELL_SIZE))
                    territory_surface.blit(text_surface, text_rect)
            
            # Draw solid rectangles for white territory
            for point, influence in territory_data['white']:
                x, y = point
                # Calculate rectangle size based on influence strength (0.3 to 0.9)
                normalized_influence = 0.3 + (min(abs(influence), 10) / 10) * 0.6
                rect_size = int(CELL_SIZE * normalized_influence)
                
                rect_x = board_x_offset + x * CELL_SIZE - rect_size // 2
                rect_y = board_y_offset + y * CELL_SIZE - rect_size // 2
                pygame.draw.rect(territory_surface, (255, 255, 255, 180), (rect_x, rect_y, rect_size, rect_size))
                
                # Draw a number indicating the influence strength (if enabled)
                if show_influence_numbers:
                    font = pygame.font.SysFont('Arial', 10)
                    text = f"{abs(influence):.1f}"
                    text_surface = font.render(text, True, (255, 0, 0))
                    text_rect = text_surface.get_rect(center=(board_x_offset + x * CELL_SIZE, board_y_offset + y * CELL_SIZE))
                    territory_surface.blit(text_surface, text_rect)
            
            # Blit the territory surface onto the screen
            screen.blit(territory_surface, (0, 0))
        
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
        
        # Draw the evaluate button
        button_color = (100, 200, 100) if show_territory else (150, 150, 150)
        pygame.draw.rect(screen, button_color, evaluate_button_rect)
        pygame.draw.rect(screen, (0, 0, 0), evaluate_button_rect, 2)  # Button border
        
        # Button text
        font = pygame.font.SysFont('Arial', 16)
        button_text = "Hide Territory" if show_territory else "Show Territory"
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=evaluate_button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Create a button to toggle influence numbers (if territory is shown)
        if show_territory:
            numbers_button_rect = pygame.Rect(20, 70, 150, 40)
            pygame.draw.rect(screen, (50, 150, 200), numbers_button_rect)
            numbers_text = font.render("Hide Numbers" if show_influence_numbers else "Show Numbers", True, (0, 0, 0))
            screen.blit(numbers_text, (numbers_button_rect.centerx - numbers_text.get_width() // 2, numbers_button_rect.centery - numbers_text.get_height() // 2))
            
            # Create a button to toggle potential territory
            potential_button_rect = pygame.Rect(20, 120, 150, 40)
            pygame.draw.rect(screen, (200, 150, 50), potential_button_rect)
            potential_text = font.render("Basic Territory" if potential_territory else "Potential Territory", True, (0, 0, 0))
            screen.blit(potential_text, (potential_button_rect.centerx - potential_text.get_width() // 2, potential_button_rect.centery - potential_text.get_height() // 2))
        
        # Display territory counts if evaluation is shown
        if show_territory and game_state.influence_map is not None:
            territory = game_state.get_territory_ownership()
            territory_text = f"B: {territory[BLACK]} | W: {territory[WHITE]} | Neutral: {territory[EMPTY]}"
            territory_surface = font.render(territory_text, True, (0, 0, 0))
            screen.blit(territory_surface, (evaluate_button_x, evaluate_button_y + button_height + 5))
        
        # Display current player with stone icon
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
        
        # Update the display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
