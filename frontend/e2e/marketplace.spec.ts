import { test, expect } from '@playwright/test';
import { testUsers, testProducts, testOrders, testSelectors, testHelpers } from './utils/test-data';

test.describe('Marketplace E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('farmer creates and lists a product', async ({ page }) => {
    const farmer = testUsers.farmer;
    await testHelpers.loginUser(page, farmer);
    
    await page.goto('/farmer/products/new');
    
    const product = testProducts.tomatoes;
    await page.fill('[data-testid="product-name-input"]', product.name);
    await page.fill('[data-testid="product-price-input"]', product.price.toString());
    await page.fill('[data-testid="product-quantity-input"]', product.quantity.toString());
    await page.selectOption('[data-testid="product-category-select"]', product.category);
    await page.fill('[data-testid="product-description-input"]', product.description);
    
    await page.setInputFiles('[data-testid="product-image-input"]', product.image);
    
    await page.click('[data-testid="product-submit-button"]');
    
    await page.waitForSelector(testSelectors.products.card);
    
    await expect(page.locator(`text=${product.name}`)).toBeVisible();
    await expect(page.locator(`text=$${product.price}`)).toBeVisible();
  });

  test('buyer purchases a product', async ({ page }) => {
    const buyer = testUsers.buyer;
    await testHelpers.loginUser(page, buyer);
    
    await page.goto('/products');
    
    await page.waitForSelector(testSelectors.products.card);
    
    await page.click(testSelectors.products.addToCart);
    
    await page.waitForSelector(testSelectors.cart.container);
    
    await expect(page.locator(testSelectors.cart.items)).toBeVisible();
    
    await page.click(testSelectors.cart.checkout);
    
    await page.waitForSelector('[data-testid="checkout-form"]');
    
    await page.fill('[data-testid="shipping-address"]', testOrders.order1.shippingAddress);
    await page.selectOption('[data-testid="payment-method"]', testOrders.order1.paymentMethod);
    
    await page.click('[data-testid="place-order-button"]');
    
    await page.waitForSelector('[data-testid="order-success"]');
    
    await expect(page.locator('text=Order placed successfully')).toBeVisible();
  });

  test('product search and filtering', async ({ page }) => {
    await page.goto('/products');
    
    await page.waitForSelector(testSelectors.products.list);
    
    await page.fill(testSelectors.products.search, 'tomato');
    
    await page.waitForTimeout(1000);
    
    const productCards = await page.locator(testSelectors.products.card);
    const count = await productCards.count();
    expect(count).toBeGreaterThan(0);
    
    await page.selectOption('[data-testid="category-filter"]', 'vegetables');
    
    await page.waitForTimeout(1000);
    
    const filteredCards = await page.locator(testSelectors.products.card);
    const filteredCount = await filteredCards.count();
    expect(filteredCount).toBeGreaterThan(0);
  });

  test('cart functionality', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.goto('/products');
    
    await page.waitForSelector(testSelectors.products.card);
    
    await page.click(testSelectors.products.addToCart);
    
    await page.waitForSelector(testSelectors.cart.container);
    
    const cartItems = await page.locator(testSelectors.cart.items);
    expect(await cartItems.count()).toBe(1);
    
    await page.fill(testSelectors.cart.quantity, '2');
    
    const total = await page.locator(testSelectors.cart.total);
    const totalText = await total.textContent();
    expect(totalText).toContain('$');
    
    await page.click(testSelectors.cart.remove);
    
    await page.waitForSelector('[data-testid="empty-cart-message"]');
    
    await expect(page.locator('text=Your cart is empty')).toBeVisible();
  });

  test('order tracking and status updates', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.goto('/orders');
    
    await page.waitForSelector(testSelectors.orders.list);
    
    const firstOrder = await page.locator('[data-testid="order-item"]').first();
    await firstOrder.click();
    
    await page.waitForSelector(testSelectors.orders.details);
    
    await expect(page.locator(testSelectors.orders.status)).toBeVisible();
    
    await expect(page.locator(testSelectors.orders.tracking)).toBeVisible();
  });

  test('mobile marketplace experience', async ({ page, context }) => {
    await context.addCookies([{
      name: 'auth-token',
      value: 'test-token',
      domain: 'localhost',
      path: '/'
    }]);
    
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/products');
    
    await page.waitForSelector(testSelectors.products.card);
    
    await page.click(testSelectors.products.addToCart);
    
    await page.waitForSelector(testSelectors.cart.container);
    
    await expect(page.locator(testSelectors.cart.items)).toBeVisible();
    
    await page.click('[data-testid="mobile-menu-button"]');
    
    await page.waitForSelector('[data-testid="mobile-sidebar"]');
    
    await expect(page.locator('[data-testid="mobile-sidebar"]')).toBeVisible();
  });

  test('marketplace performance', async ({ page }) => {
    await page.goto('/products');
    
    const startTime = Date.now();
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000);
    
    await page.fill(testSelectors.products.search, 'fresh');
    
    await page.waitForTimeout(1000);
    
    const searchStartTime = Date.now();
    await page.waitForSelector(testSelectors.products.list);
    const searchTime = Date.now() - searchStartTime;
    
    expect(searchTime).toBeLessThan(1000);
  });
});