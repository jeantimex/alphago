#!/usr/bin/env python3
"""
AlphaGo Implementation - Main Game File
A PyGame-based implementation of the Go board game with basic game mechanics.
"""

import pygame
import sys
from game.board import Board
from game.constants import BLACK, WHITE, BOARD_SIZE, CELL_SIZE, BOARD_PADDING
from game.game_state import GameState

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    board_width = BOARD_SIZE * CELL_SIZE + 2 * BOARD_PADDING
    board_height = BOARD_SIZE * CELL_SIZE + 2 * BOARD_PADDING
    screen = pygame.display.set_mode((board_width, board_height))
    pygame.display.set_caption("AlphaGo Implementation")
    
    # Create game objects
    board = Board(BOARD_SIZE)
    game_state = GameState(board)
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Get board coordinates from mouse position
                    x, y = event.pos
                    board_x = round((x - BOARD_PADDING) / CELL_SIZE)
                    board_y = round((y - BOARD_PADDING) / CELL_SIZE)
                    
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
                    print("Game reset")
        
        # Draw the board
        screen.fill((240, 217, 181))  # Wooden background color
        
        # Draw grid lines
        for i in range(BOARD_SIZE):
            # Vertical lines
            pygame.draw.line(
                screen, 
                (0, 0, 0), 
                (BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING), 
                (BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE),
                2 if i == 0 or i == BOARD_SIZE - 1 else 1
            )
            # Horizontal lines
            pygame.draw.line(
                screen, 
                (0, 0, 0), 
                (BOARD_PADDING, BOARD_PADDING + i * CELL_SIZE), 
                (BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE),
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
                (BOARD_PADDING + x * CELL_SIZE, BOARD_PADDING + y * CELL_SIZE), 
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
                        (BOARD_PADDING + x * CELL_SIZE, BOARD_PADDING + y * CELL_SIZE), 
                        CELL_SIZE // 2 - 1
                    )
        
        # Display current player
        font = pygame.font.SysFont('Arial', 20)
        player_text = f"Current Player: {'Black' if game_state.current_player == BLACK else 'White'}"
        text_surface = font.render(player_text, True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))
        
        # Update the display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
