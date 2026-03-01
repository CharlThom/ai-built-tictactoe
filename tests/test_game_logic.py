import unittest
from src.game_logic import check_winner, is_board_full, check_draw, update_game_status


class TestGameLogic(unittest.TestCase):
    
    def test_check_winner_row(self):
        board = [
            ['X', 'X', 'X'],
            ['O', 'O', None],
            [None, None, None]
        ]
        self.assertEqual(check_winner(board), 'X')
    
    def test_check_winner_column(self):
        board = [
            ['O', 'X', None],
            ['O', 'X', None],
            ['O', None, None]
        ]
        self.assertEqual(check_winner(board), 'O')
    
    def test_check_winner_diagonal(self):
        board = [
            ['X', 'O', 'O'],
            ['O', 'X', None],
            [None, None, 'X']
        ]
        self.assertEqual(check_winner(board), 'X')
    
    def test_check_winner_none(self):
        board = [
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertIsNone(check_winner(board))
    
    def test_is_board_full_true(self):
        board = [
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertTrue(is_board_full(board))
    
    def test_is_board_full_false(self):
        board = [
            ['X', 'O', None],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertFalse(is_board_full(board))
    
    def test_check_draw_true(self):
        board = [
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertTrue(check_draw(board))
    
    def test_check_draw_false_not_full(self):
        board = [
            ['X', 'O', None],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertFalse(check_draw(board))
    
    def test_check_draw_false_has_winner(self):
        board = [
            ['X', 'X', 'X'],
            ['O', 'O', None],
            ['O', None, None]
        ]
        self.assertFalse(check_draw(board))
    
    def test_update_game_status_draw(self):
        board = [
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O']
        ]
        self.assertEqual(update_game_status(board, 'in_progress'), 'draw')
    
    def test_update_game_status_winner(self):
        board = [
            ['X', 'X', 'X'],
            ['O', 'O', None],
            [None, None, None]
        ]
        self.assertEqual(update_game_status(board, 'in_progress'), 'X_wins')
    
    def test_update_game_status_in_progress(self):
        board = [
            ['X', 'O', None],
            ['O', 'X', None],
            [None, None, None]
        ]
        self.assertEqual(update_game_status(board, 'in_progress'), 'in_progress')


if __name__ == '__main__':
    unittest.main()