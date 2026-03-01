const { test, expect } = require('@playwright/test');

test.describe('Game State Reset Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should reset all game state properties', async ({ page }) => {
    // Make moves to change state
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-1"]').click();
    await page.locator('[data-testid="cell-2"]').click();

    // Restart
    await page.locator('[data-testid="restart-button"]').click();

    // Verify board state
    const cells = await page.locator('[data-testid^="cell-"]').all();
    expect(cells.length).toBe(9);
    for (const cell of cells) {
      await expect(cell).toBeEmpty();
    }

    // Verify turn indicator
    const status = page.locator('[data-testid="game-status"]');
    await expect(status).toContainText(/X/i);

    // Verify no winner
    await expect(status).not.toContainText(/win/i);
    await expect(status).not.toContainText(/draw/i);
  });

  test('should reset move counter', async ({ page }) => {
    // Make several moves
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-1"]').click();
    await page.locator('[data-testid="cell-2"]').click();
    await page.locator('[data-testid="cell-3"]').click();

    // Check move counter if displayed
    const moveCounter = page.locator('[data-testid="move-counter"]');
    if (await moveCounter.isVisible()) {
      await expect(moveCounter).toContainText(/4|move/i);
    }

    // Restart
    await page.locator('[data-testid="restart-button"]').click();

    // Verify counter reset
    if (await moveCounter.isVisible()) {
      await expect(moveCounter).toContainText(/0/i);
    }
  });

  test('should allow full game after reset', async ({ page }) => {
    // Play partial game
    await page.locator('[data-testid="cell-4"]').click();
    await page.locator('[data-testid="cell-0"]').click();

    // Restart
    await page.locator('[data-testid="restart-button"]').click();

    // Play complete winning game
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-3"]').click(); // O
    await page.locator('[data-testid="cell-1"]').click(); // X
    await page.locator('[data-testid="cell-4"]').click(); // O
    await page.locator('[data-testid="cell-2"]').click(); // X wins

    // Verify win
    const status = page.locator('[data-testid="game-status"]');
    await expect(status).toContainText(/X.*win|winner.*X/i);
  });

  test('should reset game history/score if present', async ({ page }) => {
    const scoreX = page.locator('[data-testid="score-x"]');
    const scoreO = page.locator('[data-testid="score-o"]');

    // Play winning game for X
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-3"]').click();
    await page.locator('[data-testid="cell-1"]').click();
    await page.locator('[data-testid="cell-4"]').click();
    await page.locator('[data-testid="cell-2"]').click();

    // Restart (should only reset board, not score)
    await page.locator('[data-testid="restart-button"]').click();

    // Verify board is clear but score persists (if implemented)
    for (let i = 0; i < 9; i++) {
      await expect(page.locator(`[data-testid="cell-${i}"]`)).toBeEmpty();
    }
  });

  test('should handle rapid restart clicks', async ({ page }) => {
    const restartButton = page.locator('[data-testid="restart-button"]');

    // Make a move
    await page.locator('[data-testid="cell-0"]').click();

    // Click restart multiple times rapidly
    await restartButton.click();
    await restartButton.click();
    await restartButton.click();

    // Verify stable state
    for (let i = 0; i < 9; i++) {
      await expect(page.locator(`[data-testid="cell-${i}"]`)).toBeEmpty();
    }

    const status = page.locator('[data-testid="game-status"]');
    await expect(status).toContainText(/X.*turn|player X/i);
  });

  test('should reset disabled state of cells after win', async ({ page }) => {
    // Play winning game
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-3"]').click();
    await page.locator('[data-testid="cell-1"]').click();
    await page.locator('[data-testid="cell-4"]').click();
    await page.locator('[data-testid="cell-2"]').click();

    // Try clicking empty cell after win (should not work)
    const cell5Before = await page.locator('[data-testid="cell-5"]').textContent();
    await page.locator('[data-testid="cell-5"]').click();
    const cell5After = await page.locator('[data-testid="cell-5"]').textContent();
    expect(cell5Before).toBe(cell5After);

    // Restart
    await page.locator('[data-testid="restart-button"]').click();

    // Verify cells are clickable
    await page.locator('[data-testid="cell-5"]').click();
    await expect(page.locator('[data-testid="cell-5"]')).toContainText(/X/i);
  });

  test('should preserve game settings after restart', async ({ page }) => {
    // Check if theme/settings persist
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    
    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      const bodyClass = await page.locator('body').getAttribute('class');
      
      // Make moves and restart
      await page.locator('[data-testid="cell-0"]').click();
      await page.locator('[data-testid="restart-button"]').click();
      
      // Verify theme persists
      const bodyClassAfter = await page.locator('body').getAttribute('class');
      expect(bodyClassAfter).toBe(bodyClass);
    }
  });

  test('should reset with keyboard shortcut if implemented', async ({ page }) => {
    // Make moves
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-1"]').click();

    // Try common restart shortcuts
    await page.keyboard.press('r');
    await page.waitForTimeout(100);

    // Check if reset occurred (may not be implemented)
    const cell0 = await page.locator('[data-testid="cell-0"]').textContent();
    
    // If keyboard shortcut works, cells should be empty
    // Otherwise, use button
    if (cell0 !== '') {
      await page.locator('[data-testid="restart-button"]').click();
    }

    // Verify reset
    await expect(page.locator('[data-testid="cell-0"]')).toBeEmpty();
  });
});
