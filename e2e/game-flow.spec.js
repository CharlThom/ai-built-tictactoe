const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('TicTacToe Complete Game Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('should allow players to make moves with turn alternation', async ({ page }) => {
    await page.click('[data-testid="cell-0"]');
    await expect(page.locator('[data-testid="cell-0"]')).toHaveText('X');
    await expect(page.locator('[data-testid="current-player"]')).toHaveText('O');

    await page.click('[data-testid="cell-1"]');
    await expect(page.locator('[data-testid="cell-1"]')).toHaveText('O');
    await expect(page.locator('[data-testid="current-player"]')).toHaveText('X');

    await page.click('[data-testid="cell-2"]');
    await expect(page.locator('[data-testid="cell-2"]')).toHaveText('X');
    await expect(page.locator('[data-testid="current-player"]')).toHaveText('O');
  });

  test('should prevent clicking on already filled cells', async ({ page }) => {
    await page.click('[data-testid="cell-0"]');
    await expect(page.locator('[data-testid="cell-0"]')).toHaveText('X');

    await page.click('[data-testid="cell-0"]');
    await expect(page.locator('[data-testid="cell-0"]')).toHaveText('X');
    await expect(page.locator('[data-testid="current-player"]')).toHaveText('O');
  });

  test('should detect win - top row (0,1,2)', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-3"]'); // O
    await page.click('[data-testid="cell-1"]'); // X
    await page.click('[data-testid="cell-4"]'); // O
    await page.click('[data-testid="cell-2"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
    await expect(page.locator('[data-testid="cell-0"]')).toHaveClass(/winning-cell/);
    await expect(page.locator('[data-testid="cell-1"]')).toHaveClass(/winning-cell/);
    await expect(page.locator('[data-testid="cell-2"]')).toHaveClass(/winning-cell/);
  });

  test('should detect win - middle row (3,4,5)', async ({ page }) => {
    await page.click('[data-testid="cell-3"]'); // X
    await page.click('[data-testid="cell-0"]'); // O
    await page.click('[data-testid="cell-4"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-5"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect win - bottom row (6,7,8)', async ({ page }) => {
    await page.click('[data-testid="cell-6"]'); // X
    await page.click('[data-testid="cell-0"]'); // O
    await page.click('[data-testid="cell-7"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-8"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect win - left column (0,3,6)', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-3"]'); // X
    await page.click('[data-testid="cell-2"]'); // O
    await page.click('[data-testid="cell-6"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect win - middle column (1,4,7)', async ({ page }) => {
    await page.click('[data-testid="cell-1"]'); // X
    await page.click('[data-testid="cell-0"]'); // O
    await page.click('[data-testid="cell-4"]'); // X
    await page.click('[data-testid="cell-2"]'); // O
    await page.click('[data-testid="cell-7"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect win - right column (2,5,8)', async ({ page }) => {
    await page.click('[data-testid="cell-2"]'); // X
    await page.click('[data-testid="cell-0"]'); // O
    await page.click('[data-testid="cell-5"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-8"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect win - diagonal top-left to bottom-right (0,4,8)', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-4"]'); // X
    await page.click('[data-testid="cell-2"]'); // O
    await page.click('[data-testid="cell-8"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect win - diagonal top-right to bottom-left (2,4,6)', async ({ page }) => {
    await page.click('[data-testid="cell-2"]'); // X
    await page.click('[data-testid="cell-0"]'); // O
    await page.click('[data-testid="cell-4"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-6"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');
  });

  test('should detect draw when board is full with no winner', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="cell-2"]'); // X
    await page.click('[data-testid="cell-4"]'); // O
    await page.click('[data-testid="cell-3"]'); // X
    await page.click('[data-testid="cell-5"]'); // O
    await page.click('[data-testid="cell-7"]'); // X
    await page.click('[data-testid="cell-6"]'); // O
    await page.click('[data-testid="cell-8"]'); // X

    await expect(page.locator('[data-testid="game-status"]')).toHaveText("It's a draw!");
  });

  test('should allow player O to win', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-3"]'); // O
    await page.click('[data-testid="cell-1"]'); // X
    await page.click('[data-testid="cell-4"]'); // O
    await page.click('[data-testid="cell-6"]'); // X
    await page.click('[data-testid="cell-5"]'); // O wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player O wins!');
  });

  test('should reset game when reset button is clicked', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-1"]'); // O
    await page.click('[data-testid="reset-button"]');

    await expect(page.locator('[data-testid="cell-0"]')).toHaveText('');
    await expect(page.locator('[data-testid="cell-1"]')).toHaveText('');
    await expect(page.locator('[data-testid="current-player"]')).toHaveText('X');
    await expect(page.locator('[data-testid="game-status"]')).toHaveText('');
  });

  test('should prevent moves after game is won', async ({ page }) => {
    await page.click('[data-testid="cell-0"]'); // X
    await page.click('[data-testid="cell-3"]'); // O
    await page.click('[data-testid="cell-1"]'); // X
    await page.click('[data-testid="cell-4"]'); // O
    await page.click('[data-testid="cell-2"]'); // X wins

    await expect(page.locator('[data-testid="game-status"]')).toHaveText('Player X wins!');

    await page.click('[data-testid="cell-5"]');
    await expect(page.locator('[data-testid="cell-5"]')).toHaveText('');
  });
});
