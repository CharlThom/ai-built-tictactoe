def check_winner(board):
    """
    Check if there's a winner on the board.
    
    Args:
        board: 3x3 array representing the game board
        
    Returns:
        'X' if X wins, 'O' if O wins, 'draw' if board is full with no winner, None if game continues
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]
    
    # Check diagonal (top-left to bottom-right)
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    
    # Check diagonal (top-right to bottom-left)
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    
    # Check for draw (board full)
    is_full = all(cell is not None for row in board for cell in row)
    if is_full:
        return 'draw'
    
    # Game continues
    return None