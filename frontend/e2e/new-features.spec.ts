import { test, expect } from '@playwright/test';

test.describe('Social Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/community');
  });

  test('should display community page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Community');
  });

  test('should create a post', async ({ page }) => {
    const postContent = 'Test post from Playwright';
    
    await page.fill('textarea[placeholder*="Share something"]', postContent);
    await page.click('button:has-text("Post")');
    
    await expect(page.locator('text=' + postContent).first()).toBeVisible();
  });

  test('should like a post', async ({ page }) => {
    await page.waitForSelector('button:has-text("❤️")', { timeout: 5000 });
    
    const likeButton = page.locator('button:has-text("❤️")').first();
    const initialCount = await likeButton.textContent();
    
    await likeButton.click();
    await page.waitForTimeout(500);
    
    const newCount = await likeButton.textContent();
    expect(newCount).not.toBe(initialCount);
  });

  test('should add a comment', async ({ page }) => {
    await page.click('button:has-text("💬")').first();
    await page.waitForSelector('input[placeholder*="Add a comment"]');
    
    await page.fill('input[placeholder*="Add a comment"]', 'Test comment');
    await page.click('button:has-text("Comment")');
    
    await expect(page.locator('text=Test comment')).toBeVisible();
  });
});

test.describe('Supply Chain Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/supply-chain');
  });

  test('should display supply chain page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Supply Chain Tracking');
  });

  test('should track new product', async ({ page }) => {
    await page.click('button:has-text("Track New Product")');
    
    await page.fill('input[placeholder="Product Name"]', 'Test Tomatoes');
    await page.fill('input[placeholder="Origin Location"]', 'Farm A');
    await page.fill('input[placeholder="Current Location"]', 'Farm A');
    await page.fill('input[placeholder="Notes"]', 'Fresh harvest');
    
    await page.click('button:has-text("Add Product")');
    
    await expect(page.locator('text=Test Tomatoes')).toBeVisible();
  });

  test('should view tracking details', async ({ page }) => {
    await page.waitForSelector('text=Tracked Products', { timeout: 5000 });
    
    const product = page.locator('.border').first();
    if (await product.isVisible()) {
      await product.click();
      await expect(page.locator('text=Tracking Details')).toBeVisible();
    }
  });
});

test.describe('Blockchain Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/blockchain');
  });

  test('should display blockchain page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Blockchain Transparency');
  });

  test('should show statistics', async ({ page }) => {
    await expect(page.locator('text=Total Transactions')).toBeVisible();
    await expect(page.locator('text=Total Value')).toBeVisible();
    await expect(page.locator('text=Active Users')).toBeVisible();
  });

  test('should create transaction', async ({ page }) => {
    await page.click('button:has-text("New Transaction")');
    
    await page.fill('input[placeholder="Recipient Address"]', '0xtest123');
    await page.fill('input[placeholder="Amount"]', '100');
    
    await page.click('button:has-text("Send Transaction")');
    
    await expect(page.locator('text=0xtest123')).toBeVisible();
  });

  test('should display transaction history', async ({ page }) => {
    await expect(page.locator('text=Transaction History')).toBeVisible();
  });
});

test.describe('Integration Tests', () => {
  test('should navigate between new features', async ({ page }) => {
    await page.goto('/community');
    await expect(page.locator('h1')).toContainText('Community');
    
    await page.goto('/supply-chain');
    await expect(page.locator('h1')).toContainText('Supply Chain');
    
    await page.goto('/blockchain');
    await expect(page.locator('h1')).toContainText('Blockchain');
  });

  test('should be responsive', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/community');
    await expect(page.locator('h1')).toBeVisible();
    
    await page.goto('/supply-chain');
    await expect(page.locator('h1')).toBeVisible();
    
    await page.goto('/blockchain');
    await expect(page.locator('h1')).toBeVisible();
  });
});
