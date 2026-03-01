def check_winner(board):
    """
    Check if there's a winner on the board.
    Returns 'X', 'O', or None
    """
    # Check rows
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not None:
            return board[row][0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    
    return None


def is_board_full(board):
    """
    Check if the board is completely filled.
    Returns True if full, False otherwise
    """
    for row in board:
        for cell in row:
            if cell is None:
                return False
    return True


def check_draw(board):
    """
    Check if the game is a draw (board full with no winner).
    Returns True if draw, False otherwise
    """
    if is_board_full(board) and check_winner(board) is None:
        return True
    return False


def update_game_status(board, current_status):
    """
    Update game status based on current board state.
    Returns updated status: 'in_progress', 'draw', 'X_wins', or 'O_wins'
    """
    if current_status != 'in_progress':
        return current_status
    
    winner = check_winner(board)
    if winner:
        return f'{winner}_wins'
    
    if check_draw(board):
        return 'draw'
    
    return 'in_progress'