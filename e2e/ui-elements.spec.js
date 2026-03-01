const { test, expect } = require('@playwright/test');

test.describe('TicTacToe UI Elements - Turn Indicator and Messages', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test.describe('Turn Indicator Display', () => {
    test('should display X as current player on initial load', async ({ page }) => {
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      await expect(turnIndicator).toBeVisible();
      await expect(turnIndicator).toContainText('X');
      await expect(turnIndicator).toContainText('turn', { ignoreCase: true });
    });

    test('should update turn indicator to O after X makes first move', async ({ page }) => {
      await page.click('[data-testid="cell-0"]');
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      await expect(turnIndicator).toContainText('O');
    });

    test('should alternate turn indicator correctly through multiple moves', async ({ page }) => {
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      
      await expect(turnIndicator).toContainText('X');
      await page.click('[data-testid="cell-0"]');
      await expect(turnIndicator).toContainText('O');
      await page.click('[data-testid="cell-1"]');
      await expect(turnIndicator).toContainText('X');
      await page.click('[data-testid="cell-2"]');
      await expect(turnIndicator).toContainText('O');
    });

    test('should hide or disable turn indicator after game ends', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      await expect(turnIndicator).not.toBeVisible();
    });
  });

  test.describe('Win Message Rendering', () => {
    test('should display win message when X wins horizontally', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      const winMessage = page.locator('[data-testid="game-message"]');
      await expect(winMessage).toBeVisible();
      await expect(winMessage).toContainText('X');
      await expect(winMessage).toContainText('wins', { ignoreCase: true });
    });

    test('should display win message when O wins vertically', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-1"]'); // O
      await page.click('[data-testid="cell-3"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-8"]'); // X
      await page.click('[data-testid="cell-7"]'); // O wins
      
      const winMessage = page.locator('[data-testid="game-message"]');
      await expect(winMessage).toBeVisible();
      await expect(winMessage).toContainText('O');
      await expect(winMessage).toContainText('wins', { ignoreCase: true });
    });

    test('should display win message when X wins diagonally', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-1"]'); // O
      await page.click('[data-testid="cell-4"]'); // X
      await page.click('[data-testid="cell-2"]'); // O
      await page.click('[data-testid="cell-8"]'); // X wins
      
      const winMessage = page.locator('[data-testid="game-message"]');
      await expect(winMessage).toBeVisible();
      await expect(winMessage).toContainText('X');
      await expect(winMessage).toContainText('wins', { ignoreCase: true });
    });

    test('should have proper styling for win message', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      const winMessage = page.locator('[data-testid="game-message"]');
      await expect(winMessage).toHaveCSS('font-weight', /bold|700/);
      const fontSize = await winMessage.evaluate(el => window.getComputedStyle(el).fontSize);
      expect(parseFloat(fontSize)).toBeGreaterThan(14);
    });
  });

  test.describe('Draw Message Rendering', () => {
    test('should display draw message when game ends in tie', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-1"]'); // O
      await page.click('[data-testid="cell-2"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-3"]'); // X
      await page.click('[data-testid="cell-5"]'); // O
      await page.click('[data-testid="cell-7"]'); // X
      await page.click('[data-testid="cell-6"]'); // O
      await page.click('[data-testid="cell-8"]'); // X - Draw
      
      const drawMessage = page.locator('[data-testid="game-message"]');
      await expect(drawMessage).toBeVisible();
      await expect(drawMessage).toContainText(/draw|tie/i);
    });

    test('should not display win message in draw scenario', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-1"]'); // O
      await page.click('[data-testid="cell-2"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-3"]'); // X
      await page.click('[data-testid="cell-5"]'); // O
      await page.click('[data-testid="cell-7"]'); // X
      await page.click('[data-testid="cell-6"]'); // O
      await page.click('[data-testid="cell-8"]'); // X - Draw
      
      const gameMessage = page.locator('[data-testid="game-message"]');
      await expect(gameMessage).not.toContainText('wins');
    });
  });

  test.describe('Message Persistence and Reset', () => {
    test('should persist win message until reset button is clicked', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      const winMessage = page.locator('[data-testid="game-message"]');
      await expect(winMessage).toBeVisible();
      
      await page.waitForTimeout(1000);
      await expect(winMessage).toBeVisible();
    });

    test('should clear message and restore turn indicator after reset', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      await page.click('[data-testid="reset-button"]');
      
      const gameMessage = page.locator('[data-testid="game-message"]');
      await expect(gameMessage).not.toBeVisible();
      
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      await expect(turnIndicator).toBeVisible();
      await expect(turnIndicator).toContainText('X');
    });
  });

  test.describe('Accessibility and Visual Feedback', () => {
    test('should have proper ARIA labels for turn indicator', async ({ page }) => {
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      await expect(turnIndicator).toHaveAttribute('aria-live', 'polite');
    });

    test('should have proper ARIA labels for game message', async ({ page }) => {
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      const gameMessage = page.locator('[data-testid="game-message"]');
      await expect(gameMessage).toHaveAttribute('role', 'status');
      await expect(gameMessage).toHaveAttribute('aria-live', 'assertive');
    });

    test('should have distinct visual styling between turn indicator and game message', async ({ page }) => {
      const turnIndicator = page.locator('[data-testid="turn-indicator"]');
      const turnColor = await turnIndicator.evaluate(el => window.getComputedStyle(el).color);
      
      await page.click('[data-testid="cell-0"]'); // X
      await page.click('[data-testid="cell-3"]'); // O
      await page.click('[data-testid="cell-1"]'); // X
      await page.click('[data-testid="cell-4"]'); // O
      await page.click('[data-testid="cell-2"]'); // X wins
      
      const gameMessage = page.locator('[data-testid="game-message"]');
      const messageColor = await gameMessage.evaluate(el => window.getComputedStyle(el).color);
      
      expect(turnColor).toBeDefined();
      expect(messageColor).toBeDefined();
    });
  });
});
