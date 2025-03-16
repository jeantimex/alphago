"""
SGF (Smart Game Format) parser for the Go game implementation.
Handles loading and parsing SGF files for Go games.
"""

import re
from .constants import BLACK, WHITE, EMPTY, BOARD_SIZE

class SGFParser:
    """
    Parser for SGF (Smart Game Format) files, commonly used for Go game records.
    """
    
    def __init__(self):
        """Initialize the SGF parser."""
        self.properties = {}
        self.moves = []
        self.board_size = BOARD_SIZE
        self.sgf_content = ""
    
    def parse_file(self, file_path):
        """
        Parse an SGF file.
        
        Args:
            file_path (str): Path to the SGF file
            
        Returns:
            dict: Parsed game information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.sgf_content = f.read()
            return self.parse_content(self.sgf_content)
        except UnicodeDecodeError:
            # Try with different encodings if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='iso-8859-1') as f:
                    self.sgf_content = f.read()
                return self.parse_content(self.sgf_content)
            except Exception as e:
                print(f"Error parsing SGF file: {e}")
                return None
        except Exception as e:
            print(f"Error opening SGF file: {e}")
            return None
    
    def parse_content(self, content):
        """
        Parse SGF content.
        
        Args:
            content (str): SGF content as string
            
        Returns:
            dict: Parsed game information
        """
        # Reset parser state
        self.properties = {}
        self.moves = []
        
        # Remove comments and whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'C\[.*?\]', '', content)
        
        # Extract the main game tree
        match = re.search(r'\(;(.*)\)', content)
        if not match:
            print("Invalid SGF format: No game tree found")
            return None
        
        game_tree = match.group(1)
        
        # Parse properties and moves
        self._parse_properties(game_tree)
        self._parse_moves(game_tree)
        
        # Extract board size
        if 'SZ' in self.properties:
            try:
                self.board_size = int(self.properties['SZ'][0])
            except ValueError:
                # Default to standard size if parsing fails
                self.board_size = BOARD_SIZE
        
        return {
            'properties': self.properties,
            'moves': self.moves,
            'board_size': self.board_size
        }
    
    def _parse_properties(self, game_tree):
        """
        Parse SGF properties.
        
        Args:
            game_tree (str): SGF game tree content
        """
        # Find all property value pairs (e.g., SZ[19])
        property_pattern = r'([A-Z]+)(\[.*?\])'
        
        # Extract initial properties (before the first move)
        first_move_index = game_tree.find(';', 1)
        if first_move_index == -1:
            header = game_tree
        else:
            header = game_tree[:first_move_index]
        
        for match in re.finditer(property_pattern, header):
            prop_name = match.group(1)
            prop_value = match.group(2)
            
            # Extract the value from brackets
            values = re.findall(r'\[(.*?)\]', prop_value)
            
            if prop_name not in self.properties:
                self.properties[prop_name] = values
            else:
                self.properties[prop_name].extend(values)
    
    def _parse_moves(self, game_tree):
        """
        Parse SGF moves.
        
        Args:
            game_tree (str): SGF game tree content
        """
        # Find all move nodes (starting with ;)
        nodes = game_tree.split(';')
        
        # Skip the first node (it contains the header properties)
        for node in nodes[1:]:
            # Look for B or W moves
            b_move = re.search(r'B\[(.*?)\]', node)
            w_move = re.search(r'W\[(.*?)\]', node)
            
            if b_move:
                pos = b_move.group(1)
                if pos:  # Not a pass
                    x, y = self._sgf_pos_to_coords(pos)
                    self.moves.append(('B', x, y))
                else:  # Pass
                    self.moves.append(('B', None, None))
            
            if w_move:
                pos = w_move.group(1)
                if pos:  # Not a pass
                    x, y = self._sgf_pos_to_coords(pos)
                    self.moves.append(('W', x, y))
                else:  # Pass
                    self.moves.append(('W', None, None))
    
    def _sgf_pos_to_coords(self, pos):
        """
        Convert SGF position (e.g., 'aa', 'cd') to board coordinates.
        
        Args:
            pos (str): SGF position
            
        Returns:
            tuple: (x, y) coordinates
        """
        if len(pos) < 2:
            return None, None
        
        x = ord(pos[0]) - ord('a')
        y = ord(pos[1]) - ord('a')
        
        return x, y
    
    def get_game_info(self):
        """
        Get game information from parsed SGF.
        
        Returns:
            dict: Game information
        """
        info = {
            'board_size': self.board_size,
            'moves': self.moves,
            'white_player': self.properties.get('PW', ['Unknown'])[0],
            'black_player': self.properties.get('PB', ['Unknown'])[0],
            'date': self.properties.get('DT', ['Unknown'])[0],
            'result': self.properties.get('RE', ['Unknown'])[0],
            'event': self.properties.get('EV', ['Unknown'])[0],
            'komi': float(self.properties.get('KM', ['6.5'])[0]) if 'KM' in self.properties else 6.5,
        }
        
        return info
