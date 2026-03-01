import unittest
from src.game_state import GameState, Player, GameStatus


class TestGameState(unittest.TestCase):
    """Test cases for GameState model."""
    
    def setUp(self):
        """Set up a fresh game state for each test."""
        self.game = GameState()
    
    def test_initial_state(self):
        """Test initial game state."""
        self.assertEqual(len(self.game.board), 9)
        self.assertTrue(all(cell is None for cell in self.game.board))
        self.assertEqual(self.game.current_player, Player.X)
        self.assertEqual(self.game.status, GameStatus.IN_PROGRESS)
        self.assertIsNone(self.game.winner)
    
    def test_make_valid_move(self):
        """Test making a valid move."""
        result = self.game.make_move(0)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0], Player.X)
        self.assertEqual(self.game.current_player, Player.O)
    
    def test_make_invalid_move(self):
        """Test making an invalid move."""
        self.game.make_move(0)
        result = self.game.make_move(0)  # Same position
        self.assertFalse(result)
    
    def test_player_switching(self):
        """Test that players alternate turns."""
        self.game.make_move(0)
        self.assertEqual(self.game.current_player, Player.O)
        self.game.make_move(1)
        self.assertEqual(self.game.current_player, Player.X)
    
    def test_horizontal_win(self):
        """Test horizontal win detection."""
        self.game.make_move(0)  # X
        self.game.make_move(3)  # O
        self.game.make_move(1)  # X
        self.game.make_move(4)  # O
        self.game.make_move(2)  # X wins
        self.assertEqual(self.game.status, GameStatus.X_WINS)
        self.assertEqual(self.game.winner, Player.X)
    
    def test_vertical_win(self):
        """Test vertical win detection."""
        self.game.make_move(0)  # X
        self.game.make_move(1)  # O
        self.game.make_move(3)  # X
        self.game.make_move(2)  # O
        self.game.make_move(6)  # X wins
        self.assertEqual(self.game.status, GameStatus.X_WINS)
    
    def test_diagonal_win(self):
        """Test diagonal win detection."""
        self.game.make_move(0)  # X
        self.game.make_move(1)  # O
        self.game.make_move(4)  # X
        self.game.make_move(2)  # O
        self.game.make_move(8)  # X wins
        self.assertEqual(self.game.status, GameStatus.X_WINS)
    
    def test_draw(self):
        """Test draw detection."""
        moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]
        for move in moves:
            self.game.make_move(move)
        self.assertEqual(self.game.status, GameStatus.DRAW)
        self.assertIsNone(self.game.winner)
    
    def test_reset(self):
        """Test game reset."""
        self.game.make_move(0)
        self.game.reset()
        self.assertTrue(all(cell is None for cell in self.game.board))
        self.assertEqual(self.game.current_player, Player.X)
        self.assertEqual(self.game.status, GameStatus.IN_PROGRESS)
    
    def test_to_dict(self):
        """Test dictionary serialization."""
        self.game.make_move(0)
        state_dict = self.game.to_dict()
        self.assertIn("board", state_dict)
        self.assertIn("current_player", state_dict)
        self.assertIn("status", state_dict)
        self.assertEqual(state_dict["board"][0], "X")


if __name__ == "__main__":
    unittest.main()