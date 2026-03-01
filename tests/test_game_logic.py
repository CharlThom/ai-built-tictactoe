import unittest
from src.game_logic import check_winner


class TestWinConditions(unittest.TestCase):
    
    def test_row_win(self):
        board = [
            ['X', 'X', 'X'],
            ['O', 'O', None],
            [None, None, None]
        ]
        self.assertEqual(check_winner(board), 'X')
    
    def test_column_win(self):
        board = [
            ['O', 'X', None],
            ['O', 'X', None],
            ['O', None, None]
        ]
        self.assertEqual(check_winner(board), 'O')
    
    def test_diagonal_win_top_left(self):
        board = [
            ['X', 'O', 'O'],
            ['O', 'X', None],
            [None, None, 'X']
        ]
        self.assertEqual(check_winner(board), 'X')
    
    def test_diagonal_win_top_right(self):
        board = [
            ['X', 'O', 'O'],
            ['X', 'O', None],
            ['O', None, 'X']
        ]
        self.assertEqual(check_winner(board), 'O')
    
    def test_draw(self):
        board = [
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertEqual(check_winner(board), 'draw')
    
    def test_game_in_progress(self):
        board = [
            ['X', 'O', None],
            ['O', 'X', None],
            [None, None, None]
        ]
        self.assertIsNone(check_winner(board))
    
    def test_empty_board(self):
        board = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.assertIsNone(check_winner(board))


if __name__ == '__main__':
    unittest.main()