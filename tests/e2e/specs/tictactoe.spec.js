const { test, expect } = require('@playwright/test');

test.describe('TicTacToe Game', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load game board with 9 empty cells', async ({ page }) => {
    const cells = page.locator('[data-testid="cell"]');
    await expect(cells).toHaveCount(9);
    for (let i = 0; i < 9; i++) {
      await expect(cells.nth(i)).toBeEmpty();
    }
  });

  test('should display current player turn', async ({ page }) => {
    const turnIndicator = page.locator('[data-testid="turn-indicator"]');
    await expect(turnIndicator).toContainText('Player X');
  });

  test('should allow players to make moves alternately', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText('X');
    await expect(page.locator('[data-testid="turn-indicator"]')).toContainText('Player O');
    
    await page.locator('[data-testid="cell-4"]').click();
    await expect(page.locator('[data-testid="cell-4"]')).toContainText('O');
    await expect(page.locator('[data-testid="turn-indicator"]')).toContainText('Player X');
  });

  test('should prevent clicking on occupied cells', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText('X');
    
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText('X');
    await expect(page.locator('[data-testid="turn-indicator"]')).toContainText('Player O');
  });

  test('should detect horizontal win', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-3"]').click(); // O
    await page.locator('[data-testid="cell-1"]').click(); // X
    await page.locator('[data-testid="cell-4"]').click(); // O
    await page.locator('[data-testid="cell-2"]').click(); // X wins
    
    await expect(page.locator('[data-testid="game-status"]')).toContainText('Player X wins!');
  });

  test('should detect vertical win', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-1"]').click(); // O
    await page.locator('[data-testid="cell-3"]').click(); // X
    await page.locator('[data-testid="cell-2"]').click(); // O
    await page.locator('[data-testid="cell-6"]').click(); // X wins
    
    await expect(page.locator('[data-testid="game-status"]')).toContainText('Player X wins!');
  });

  test('should detect diagonal win', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-1"]').click(); // O
    await page.locator('[data-testid="cell-4"]').click(); // X
    await page.locator('[data-testid="cell-2"]').click(); // O
    await page.locator('[data-testid="cell-8"]').click(); // X wins
    
    await expect(page.locator('[data-testid="game-status"]')).toContainText('Player X wins!');
  });

  test('should detect draw game', async ({ page }) => {
    const moves = [0, 1, 2, 4, 3, 5, 7, 6, 8];
    for (const move of moves) {
      await page.locator(`[data-testid="cell-${move}"]`).click();
    }
    
    await expect(page.locator('[data-testid="game-status"]')).toContainText('Draw');
  });

  test('should reset game when reset button clicked', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-4"]').click();
    
    await page.locator('[data-testid="reset-button"]').click();
    
    const cells = page.locator('[data-testid="cell"]');
    for (let i = 0; i < 9; i++) {
      await expect(cells.nth(i)).toBeEmpty();
    }
    await expect(page.locator('[data-testid="turn-indicator"]')).toContainText('Player X');
  });

  test('should prevent moves after game ends', async ({ page }) => {
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-3"]').click(); // O
    await page.locator('[data-testid="cell-1"]').click(); // X
    await page.locator('[data-testid="cell-4"]').click(); // O
    await page.locator('[data-testid="cell-2"]').click(); // X wins
    
    await page.locator('[data-testid="cell-5"]').click();
    await expect(page.locator('[data-testid="cell-5"]')).toBeEmpty();
  });
});