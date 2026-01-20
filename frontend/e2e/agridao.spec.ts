import { test, expect } from '@playwright/test';

test.describe('AgriDAO E2E Tests', () => {
  test('user can register and login', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Register new user
    await page.click('text=Register');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'testpassword123');
    await page.fill('[data-testid=full-name]', 'Test User');
    await page.click('[data-testid=register-button]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });
  
  test('farmer can list product', async ({ page }) => {
    // Login as farmer
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid=email]', 'farmer@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('[data-testid=login-button]');
    
    // Add product
    await page.click('text=Add Product');
    await page.fill('[data-testid=product-name]', 'Fresh Tomatoes');
    await page.fill('[data-testid=product-price]', '50');
    await page.click('[data-testid=submit-product]');
    
    // Should see success message
    await expect(page.locator('text=Product added successfully')).toBeVisible();
  });
  
  test('buyer can browse and order products', async ({ page }) => {
    await page.goto('http://localhost:3000/marketplace');
    
    // Browse products
    await expect(page.locator('[data-testid=product-card]')).toBeVisible();
    
    // Add to cart
    await page.click('[data-testid=add-to-cart]:first-child');
    
    // Go to cart and checkout
    await page.click('[data-testid=cart-icon]');
    await page.click('[data-testid=checkout-button]');
    
    // Should reach payment page
    await expect(page).toHaveURL(/.*checkout/);
  });
});
