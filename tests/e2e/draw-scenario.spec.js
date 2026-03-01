const { test, expect } = require('@playwright/test');

test.describe('TicTacToe - Draw Scenario', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should detect draw when all cells filled without winner - pattern 1', async ({ page }) => {
    // Pattern: X X O
    //          O O X
    //          X O X
    const moves = [
      { player: 'X', cell: 0 },
      { player: 'O', cell: 2 },
      { player: 'X', cell: 1 },
      { player: 'O', cell: 3 },
      { player: 'X', cell: 5 },
      { player: 'O', cell: 4 },
      { player: 'X', cell: 6 },
      { player: 'O', cell: 7 },
      { player: 'X', cell: 8 }
    ];

    for (const move of moves) {
      await page.click(`[data-testid="cell-${move.cell}"]`);
    }

    const drawMessage = page.locator('[data-testid="game-status"]');
    await expect(drawMessage).toContainText(/draw|tie/i);
    
    const allCells = page.locator('[data-testid^="cell-"]');
    await expect(allCells).toHaveCount(9);
    
    for (let i = 0; i < 9; i++) {
      const cell = page.locator(`[data-testid="cell-${i}"]`);
      await expect(cell).not.toBeEmpty();
    }
  });

  test('should detect draw when all cells filled without winner - pattern 2', async ({ page }) => {
    // Pattern: O X X
    //          X X O
    //          O O X
    const moves = [
      { player: 'X', cell: 1 },
      { player: 'O', cell: 0 },
      { player: 'X', cell: 2 },
      { player: 'O', cell: 5 },
      { player: 'X', cell: 3 },
      { player: 'O', cell: 6 },
      { player: 'X', cell: 4 },
      { player: 'O', cell: 7 },
      { player: 'X', cell: 8 }
    ];

    for (const move of moves) {
      await page.click(`[data-testid="cell-${move.cell}"]`);
    }

    await expect(page.locator('[data-testid="game-status"]')).toContainText(/draw|tie/i);
  });

  test('should disable all cells after draw', async ({ page }) => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];

    for (const cellIndex of moves) {
      await page.click(`[data-testid="cell-${cellIndex}"]`);
    }

    for (let i = 0; i < 9; i++) {
      const cell = page.locator(`[data-testid="cell-${i}"]`);
      await expect(cell).toBeDisabled();
    }
  });

  test('should allow restart after draw', async ({ page }) => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];

    for (const cellIndex of moves) {
      await page.click(`[data-testid="cell-${cellIndex}"]`);
    }

    await expect(page.locator('[data-testid="game-status"]')).toContainText(/draw|tie/i);

    const restartButton = page.locator('[data-testid="restart-button"]');
    await expect(restartButton).toBeVisible();
    await restartButton.click();

    for (let i = 0; i < 9; i++) {
      const cell = page.locator(`[data-testid="cell-${i}"]`);
      await expect(cell).toBeEmpty();
      await expect(cell).toBeEnabled();
    }

    await expect(page.locator('[data-testid="game-status"]')).toContainText(/X.*turn|next.*X/i);
  });

  test('should show correct player turns during draw scenario', async ({ page }) => {
    const moves = [
      { cell: 0, expectedNext: /O.*turn|next.*O/i },
      { cell: 2, expectedNext: /X.*turn|next.*X/i },
      { cell: 1, expectedNext: /O.*turn|next.*O/i },
      { cell: 3, expectedNext: /X.*turn|next.*X/i },
      { cell: 5, expectedNext: /O.*turn|next.*O/i },
      { cell: 4, expectedNext: /X.*turn|next.*X/i },
      { cell: 6, expectedNext: /O.*turn|next.*O/i },
      { cell: 7, expectedNext: /X.*turn|next.*X/i }
    ];

    for (const move of moves) {
      await page.click(`[data-testid="cell-${move.cell}"]`);
      await expect(page.locator('[data-testid="game-status"]')).toContainText(move.expectedNext);
    }

    await page.click('[data-testid="cell-8"]');
    await expect(page.locator('[data-testid="game-status"]')).toContainText(/draw|tie/i);
  });

  test('should not allow clicking filled cells during draw scenario', async ({ page }) => {
    await page.click('[data-testid="cell-0"]');
    await expect(page.locator('[data-testid="cell-0"]')).toContainText('X');

    await page.click('[data-testid="cell-0"]');
    await expect(page.locator('[data-testid="cell-0"]')).toContainText('X');
    await expect(page.locator('[data-testid="cell-0"]')).not.toContainText('O');
  });

  test('should maintain game state consistency throughout draw', async ({ page }) => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];
    const expectedBoard = ['X', 'X', 'O', 'O', 'O', 'X', 'X', 'O', 'X'];

    for (const cellIndex of moves) {
      await page.click(`[data-testid="cell-${cellIndex}"]`);
    }

    for (let i = 0; i < 9; i++) {
      const cell = page.locator(`[data-testid="cell-${i}"]`);
      await expect(cell).toContainText(expectedBoard[i]);
    }

    await expect(page.locator('[data-testid="game-status"]')).toContainText(/draw|tie/i);
  });
});