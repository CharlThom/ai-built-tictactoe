#!/usr/bin/env python3
"""
TicTacToe API Quickstart Example

This script demonstrates how to:
1. Initialize a new game session
2. Make moves alternating between players
3. Check game state
4. Handle game completion
5. Restart a game

Usage:
    export TICTACTOE_API_KEY="your_api_key_here"
    python quickstart_example.py
"""

import os
import sys
import requests
from typing import Dict, Optional, Tuple
import time


class TicTacToeClient:
    """Simple client for TicTacToe API"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_game(self, player1: str, player2: str, first_player: str = "X") -> Dict:
        """Initialize a new game session"""
        response = requests.post(
            f"{self.api_url}/game/new",
            headers=self.headers,
            json={
                "player1": player1,
                "player2": player2,
                "firstPlayer": first_player
            }
        )
        response.raise_for_status()
        return response.json()
    
    def make_move(self, game_id: str, player: str, row: int, col: int) -> Dict:
        """Make a move on the board"""
        response = requests.post(
            f"{self.api_url}/game/move",
            headers=self.headers,
            json={
                "gameId": game_id,
                "player": player,
                "position": {"row": row, "col": col}
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_state(self, game_id: str) -> Dict:
        """Get current game state"""
        response = requests.get(
            f"{self.api_url}/game/state/{game_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def restart_game(self, game_id: str) -> Dict:
        """Restart an existing game"""
        response = requests.post(
            f"{self.api_url}/game/restart",
            headers=self.headers,
            json={"gameId": game_id}
        )
        response.raise_for_status()
        return response.json()


def print_board(board: list):
    """Pretty print the game board"""
    print("\n  0   1   2")
    for i, row in enumerate(board):
        cells = [cell if cell else " " for cell in row]
        print(f"{i} {cells[0]} | {cells[1]} | {cells[2]}")
        if i < 2:
            print("  ---------")
    print()


def play_sample_game(client: TicTacToeClient):
    """Play a complete sample game"""
    
    print("=" * 50)
    print("TicTacToe API Quickstart Example")
    print("=" * 50)
    
    # Step 1: Create a new game
    print("\n[1] Creating new game...")
    game = client.create_game("Alice", "Bob", "X")
    game_id = game["gameId"]
    print(f"✓ Game created: {game_id}")
    print(f"  Players: {game['players']['X']} (X) vs {game['players']['O']} (O)")
    print_board(game["board"])
    
    # Step 2: Play a sequence of moves
    moves = [
        ("X", 0, 0),  # Alice
        ("O", 1, 1),  # Bob
        ("X", 0, 1),  # Alice
        ("O", 2, 2),  # Bob
        ("X", 0, 2),  # Alice - wins!
    ]
    
    print("[2] Playing moves...\n")
    for player, row, col in moves:
        player_name = game['players'][player]
        print(f"→ {player_name} ({player}) plays at position ({row}, {col})")
        
        try:
            result = client.make_move(game_id, player, row, col)
            print_board(result["board"])
            
            if result["status"] == "completed":
                if result.get("winner"):
                    winner_name = game['players'][result['winner']]
                    print(f"🎉 {winner_name} ({result['winner']}) wins!")
                    if "winningLine" in result:
                        print(f"   Winning line: {result['winningLine']}")
                else:
                    print("🤝 Game ended in a draw!")
                break
            
            time.sleep(0.5)  # Pause for readability
            
        except requests.exceptions.HTTPError as e:
            print(f"✗ Error: {e.response.json()}")
            break
    
    # Step 3: Check final game state
    print("\n[3] Checking final game state...")
    state = client.get_state(game_id)
    print(f"  Status: {state['status']}")
    print(f"  Total moves: {state.get('moveCount', 0)}")
    
    # Step 4: Restart the game
    print("\n[4] Restarting game...")
    restarted = client.restart_game(game_id)
    print(f"✓ Game restarted")
    print_board(restarted["board"])
    
    print("\n" + "=" * 50)
    print("Quickstart example completed!")
    print("=" * 50)


def main():
    # Configuration
    api_url = os.getenv("TICTACTOE_API_URL", "https://api.tictactoe.example.com/v1")
    api_key = os.getenv("TICTACTOE_API_KEY")
    
    if not api_key:
        print("Error: TICTACTOE_API_KEY environment variable not set")
        print("Usage: export TICTACTOE_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    # Initialize client
    client = TicTacToeClient(api_url, api_key)
    
    try:
        play_sample_game(client)
    except requests.exceptions.RequestException as e:
        print(f"\n✗ API Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()