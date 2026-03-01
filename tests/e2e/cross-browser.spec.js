const { test, expect, devices } = require('@playwright/test');

const browsers = ['chromium', 'firefox', 'webkit'];
const viewports = [
  { name: 'Desktop', width: 1920, height: 1080 },
  { name: 'Tablet', width: 768, height: 1024 },
  { name: 'Mobile', width: 375, height: 667 }
];

browsers.forEach(browserType => {
  test.describe(`Cross-browser testing - ${browserType}`, () => {
    
    test.use({ browserName: browserType });

    test('should render game board correctly', async ({ page }) => {
      await page.goto('/');
      
      const board = await page.locator('.game-board');
      await expect(board).toBeVisible();
      
      const cells = await page.locator('.cell');
      await expect(cells).toHaveCount(9);
      
      for (let i = 0; i < 9; i++) {
        await expect(cells.nth(i)).toBeEmpty();
      }
    });

    test('should handle player interactions correctly', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('.cell').nth(0).click();
      await expect(page.locator('.cell').nth(0)).toHaveText('X');
      
      await page.locator('.cell').nth(1).click();
      await expect(page.locator('.cell').nth(1)).toHaveText('O');
      
      const status = await page.locator('.game-status');
      await expect(status).toContainText("X's turn");
    });

    test('should detect win condition across browsers', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('.cell').nth(0).click(); // X
      await page.locator('.cell').nth(3).click(); // O
      await page.locator('.cell').nth(1).click(); // X
      await page.locator('.cell').nth(4).click(); // O
      await page.locator('.cell').nth(2).click(); // X wins
      
      const status = await page.locator('.game-status');
      await expect(status).toContainText('X wins');
      
      const winningCells = await page.locator('.cell.winning');
      await expect(winningCells).toHaveCount(3);
    });

    test('should handle reset button functionality', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('.cell').nth(0).click();
      await page.locator('.cell').nth(1).click();
      
      const resetButton = await page.locator('.reset-button');
      await resetButton.click();
      
      const cells = await page.locator('.cell');
      for (let i = 0; i < 9; i++) {
        await expect(cells.nth(i)).toBeEmpty();
      }
    });

    test('should maintain responsive layout', async ({ page }) => {
      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto('/');
        
        const board = await page.locator('.game-board');
        await expect(board).toBeVisible();
        
        const boardBox = await board.boundingBox();
        expect(boardBox.width).toBeGreaterThan(0);
        expect(boardBox.height).toBeGreaterThan(0);
        
        const cells = await page.locator('.cell');
        await expect(cells.first()).toBeVisible();
      }
    });

    test('should handle rapid clicks without errors', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('.cell').nth(0).click();
      await page.locator('.cell').nth(0).click();
      await page.locator('.cell').nth(0).click();
      
      await expect(page.locator('.cell').nth(0)).toHaveText('X');
      
      const errors = [];
      page.on('pageerror', error => errors.push(error));
      await page.waitForTimeout(500);
      expect(errors.length).toBe(0);
    });

    test('should preserve game state on page interactions', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('.cell').nth(4).click(); // X center
      await page.locator('.cell').nth(0).click(); // O corner
      
      await page.evaluate(() => window.scrollTo(0, 100));
      await page.waitForTimeout(200);
      
      await expect(page.locator('.cell').nth(4)).toHaveText('X');
      await expect(page.locator('.cell').nth(0)).toHaveText('O');
    });

    test('should handle CSS animations and transitions', async ({ page }) => {
      await page.goto('/');
      
      const cell = page.locator('.cell').nth(0);
      await cell.click();
      
      await expect(cell).toHaveText('X');
      
      const computedStyle = await cell.evaluate(el => {
        const style = window.getComputedStyle(el);
        return {
          display: style.display,
          opacity: style.opacity
        };
      });
      
      expect(parseFloat(computedStyle.opacity)).toBeGreaterThan(0);
    });
  });
});

test.describe('Browser-specific feature tests', () => {
  
  test('Safari webkit specific - touch events', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari-specific test');
    
    await page.goto('/');
    await page.setViewportSize({ width: 375, height: 667 });
    
    const cell = page.locator('.cell').nth(0);
    await cell.tap();
    await expect(cell).toHaveText('X');
  });

  test('Firefox specific - rendering consistency', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test');
    
    await page.goto('/');
    
    const board = page.locator('.game-board');
    const screenshot = await board.screenshot();
    expect(screenshot).toBeTruthy();
  });

  test('Chrome specific - performance metrics', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome-specific test');
    
    await page.goto('/');
    
    const metrics = await page.evaluate(() => {
      const perfData = window.performance.timing;
      return {
        loadTime: perfData.loadEventEnd - perfData.navigationStart,
        domReady: perfData.domContentLoadedEventEnd - perfData.navigationStart
      };
    });
    
    expect(metrics.loadTime).toBeLessThan(5000);
    expect(metrics.domReady).toBeLessThan(3000);
  });
});