import { checkWinner, hasPlayerWon, isGameOver } from './winDetection';

describe('Win Detection Algorithm', () => {
  test('detects horizontal win in top row', () => {
    const board = ['X', 'X', 'X', null, 'O', null, null, 'O', null];
    const result = checkWinner(board);
    expect(result.winner).toBe('X');
    expect(result.winningLine).toEqual([0, 1, 2]);
  });

  test('detects horizontal win in middle row', () => {
    const board = ['X', null, 'O', 'O', 'O', 'O', 'X', null, 'X'];
    const result = checkWinner(board);
    expect(result.winner).toBe('O');
    expect(result.winningLine).toEqual([3, 4, 5]);
  });

  test('detects vertical win in first column', () => {
    const board = ['X', 'O', 'O', 'X', null, null, 'X', null, null];
    const result = checkWinner(board);
    expect(result.winner).toBe('X');
    expect(result.winningLine).toEqual([0, 3, 6]);
  });

  test('detects diagonal win (top-left to bottom-right)', () => {
    const board = ['O', 'X', null, 'X', 'O', null, null, null, 'O'];
    const result = checkWinner(board);
    expect(result.winner).toBe('O');
    expect(result.winningLine).toEqual([0, 4, 8]);
  });

  test('detects diagonal win (top-right to bottom-left)', () => {
    const board = ['X', 'O', 'X', null, 'X', 'O', 'X', null, 'O'];
    const result = checkWinner(board);
    expect(result.winner).toBe('X');
    expect(result.winningLine).toEqual([2, 4, 6]);
  });

  test('detects draw when board is full with no winner', () => {
    const board = ['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X'];
    const result = checkWinner(board);
    expect(result.winner).toBe('draw');
    expect(result.winningLine).toBeNull();
  });

  test('returns null when game is in progress', () => {
    const board = ['X', 'O', null, null, 'X', null, null, null, 'O'];
    const result = checkWinner(board);
    expect(result.winner).toBeNull();
    expect(result.winningLine).toBeNull();
  });

  test('hasPlayerWon returns true for winning player', () => {
    const board = ['X', 'X', 'X', 'O', 'O', null, null, null, null];
    expect(hasPlayerWon(board, 'X')).toBe(true);
    expect(hasPlayerWon(board, 'O')).toBe(false);
  });

  test('isGameOver returns true when game ends', () => {
    const winBoard = ['X', 'X', 'X', 'O', 'O', null, null, null, null];
    const drawBoard = ['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X'];
    const activeBoard = ['X', null, null, null, 'O', null, null, null, null];
    
    expect(isGameOver(winBoard)).toBe(true);
    expect(isGameOver(drawBoard)).toBe(true);
    expect(isGameOver(activeBoard)).toBe(false);
  });
});