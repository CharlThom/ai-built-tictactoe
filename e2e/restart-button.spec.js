const { test, expect } = require('@playwright/test');

test.describe('Restart Button Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should display restart button on page load', async ({ page }) => {
    const restartButton = page.locator('[data-testid="restart-button"]');
    await expect(restartButton).toBeVisible();
    await expect(restartButton).toHaveText(/restart|new game/i);
  });

  test('should reset game state after player moves', async ({ page }) => {
    // Make some moves
    await page.locator('[data-testid="cell-0"]').click();
    await page.locator('[data-testid="cell-1"]').click();
    await page.locator('[data-testid="cell-2"]').click();

    // Verify cells are filled
    await expect(page.locator('[data-testid="cell-0"]')).toContainText(/X/i);
    await expect(page.locator('[data-testid="cell-1"]')).toContainText(/O/i);
    await expect(page.locator('[data-testid="cell-2"]')).toContainText(/X/i);

    // Click restart
    await page.locator('[data-testid="restart-button"]').click();

    // Verify all cells are empty
    for (let i = 0; i < 9; i++) {
      await expect(page.locator(`[data-testid="cell-${i}"]`)).toBeEmpty();
    }
  });

  test('should reset turn to player X after restart', async ({ page }) => {
    // Make one move (X plays)
    await page.locator('[data-testid="cell-0"]').click();
    
    // Current turn should be O
    const statusBefore = page.locator('[data-testid="game-status"]');
    await expect(statusBefore).toContainText(/O.*turn|player O/i);

    // Restart game
    await page.locator('[data-testid="restart-button"]').click();

    // Turn should be back to X
    const statusAfter = page.locator('[data-testid="game-status"]');
    await expect(statusAfter).toContainText(/X.*turn|player X/i);
  });

  test('should reset game after a win', async ({ page }) => {
    // Play a winning game for X (top row)
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-3"]').click(); // O
    await page.locator('[data-testid="cell-1"]').click(); // X
    await page.locator('[data-testid="cell-4"]').click(); // O
    await page.locator('[data-testid="cell-2"]').click(); // X wins

    // Verify win state
    const winStatus = page.locator('[data-testid="game-status"]');
    await expect(winStatus).toContainText(/X.*win|winner.*X/i);

    // Restart game
    await page.locator('[data-testid="restart-button"]').click();

    // Verify board is cleared
    for (let i = 0; i < 9; i++) {
      await expect(page.locator(`[data-testid="cell-${i}"]`)).toBeEmpty();
    }

    // Verify status is reset
    const newStatus = page.locator('[data-testid="game-status"]');
    await expect(newStatus).toContainText(/X.*turn|player X/i);

    // Verify cells are clickable again
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText(/X/i);
  });

  test('should reset game after a draw', async ({ page }) => {
    // Play a draw game
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-1"]').click(); // O
    await page.locator('[data-testid="cell-2"]').click(); // X
    await page.locator('[data-testid="cell-4"]').click(); // O
    await page.locator('[data-testid="cell-3"]').click(); // X
    await page.locator('[data-testid="cell-5"]').click(); // O
    await page.locator('[data-testid="cell-7"]').click(); // X
    await page.locator('[data-testid="cell-6"]').click(); // O
    await page.locator('[data-testid="cell-8"]').click(); // X - Draw

    // Verify draw state
    const drawStatus = page.locator('[data-testid="game-status"]');
    await expect(drawStatus).toContainText(/draw|tie/i);

    // Restart game
    await page.locator('[data-testid="restart-button"]').click();

    // Verify complete reset
    for (let i = 0; i < 9; i++) {
      await expect(page.locator(`[data-testid="cell-${i}"]`)).toBeEmpty();
    }

    const newStatus = page.locator('[data-testid="game-status"]');
    await expect(newStatus).toContainText(/X.*turn|player X/i);
  });

  test('should allow multiple restarts in succession', async ({ page }) => {
    for (let round = 0; round < 3; round++) {
      // Make a few moves
      await page.locator('[data-testid="cell-0"]').click();
      await page.locator('[data-testid="cell-4"]').click();
      
      // Verify moves were made
      await expect(page.locator('[data-testid="cell-0"]')).toContainText(/X/i);
      await expect(page.locator('[data-testid="cell-4"]')).toContainText(/O/i);

      // Restart
      await page.locator('[data-testid="restart-button"]').click();

      // Verify reset
      await expect(page.locator('[data-testid="cell-0"]')).toBeEmpty();
      await expect(page.locator('[data-testid="cell-4"]')).toBeEmpty();
    }
  });

  test('should not allow moves on filled cells after restart', async ({ page }) => {
    // Make a move
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText(/X/i);

    // Try to click same cell (should not change)
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText(/X/i);
    await expect(page.locator('[data-testid="cell-0"]')).not.toContainText(/O/i);

    // Restart
    await page.locator('[data-testid="restart-button"]').click();

    // Now cell should accept new move
    await page.locator('[data-testid="cell-0"]').click();
    await expect(page.locator('[data-testid="cell-0"]')).toContainText(/X/i);
  });

  test('should clear winning line highlight after restart', async ({ page }) => {
    // Play winning game
    await page.locator('[data-testid="cell-0"]').click(); // X
    await page.locator('[data-testid="cell-3"]').click(); // O
    await page.locator('[data-testid="cell-1"]').click(); // X
    await page.locator('[data-testid="cell-4"]').click(); // O
    await page.locator('[data-testid="cell-2"]').click(); // X wins

    // Check if winning cells have highlight class
    const winningCells = page.locator('.winning-cell, [data-winning="true"]');
    const count = await winningCells.count();
    expect(count).toBeGreaterThan(0);

    // Restart
    await page.locator('[data-testid="restart-button"]').click();

    // Verify no winning highlights
    const highlightsAfter = page.locator('.winning-cell, [data-winning="true"]');
    await expect(highlightsAfter).toHaveCount(0);
  });

  test('should maintain restart button functionality across game states', async ({ page }) => {
    const restartButton = page.locator('[data-testid="restart-button"]');

    // Initial state
    await expect(restartButton).toBeEnabled();

    // After moves
    await page.locator('[data-testid="cell-0"]').click();
    await expect(restartButton).toBeEnabled();

    // After win
    await page.locator('[data-testid="cell-3"]').click();
    await page.locator('[data-testid="cell-1"]').click();
    await page.locator('[data-testid="cell-4"]').click();
    await page.locator('[data-testid="cell-2"]').click();
    await expect(restartButton).toBeEnabled();

    // After restart
    await restartButton.click();
    await expect(restartButton).toBeEnabled();
  });
});
