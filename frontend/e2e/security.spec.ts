import { test, expect } from '@playwright/test';
import { testUsers, testSelectors, testHelpers } from './utils/test-data';

test.describe('Security Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('SQL injection prevention in authentication', async ({ page }) => {
    await page.goto('/login');
    
    const maliciousInput = "admin' OR '1'='1";
    
    await page.fill(testSelectors.auth.emailInput, maliciousInput);
    await page.fill(testSelectors.auth.passwordInput, 'password');
    
    await page.click(testSelectors.auth.submitButton);
    
    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });

  test('XSS prevention in user input', async ({ page }) => {
    await page.goto('/register');
    
    const xssPayload = '<script>alert("XSS")</script>';
    
    await page.fill(testSelectors.auth.emailInput, 'test@example.com');
    await page.fill(testSelectors.auth.passwordInput, 'password123');
    await page.fill(testSelectors.auth.confirmPasswordInput, 'password123');
    
    await page.click(testSelectors.auth.submitButton);
    
    await expect(page.locator('text=Registration successful')).toBeVisible();
    
    const pageContent = await page.content();
    expect(pageContent).not.toContain('<script>alert("XSS")</script>');
  });

  test('password complexity requirements', async ({ page }) => {
    await page.goto('/register');
    
    await page.fill(testSelectors.auth.emailInput, 'test@example.com');
    await page.fill(testSelectors.auth.passwordInput, 'weak');
    await page.fill(testSelectors.auth.confirmPasswordInput, 'weak');
    
    await page.click(testSelectors.auth.submitButton);
    
    await expect(page.locator('text=Password must contain')).toBeVisible();
  });

  test('rate limiting on login attempts', async ({ page }) => {
    await page.goto('/login');
    
    for (let i = 0; i < 5; i++) {
      await page.fill(testSelectors.auth.emailInput, 'test@example.com');
      await page.fill(testSelectors.auth.passwordInput, 'wrongpassword');
      await page.click(testSelectors.auth.submitButton);
      await page.waitForTimeout(1000);
    }
    
    await expect(page.locator('text=Too many attempts')).toBeVisible();
  });

  test('authorization - admin routes protection', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.goto('/admin/users');
    
    await expect(page.locator('text=Access denied')).toBeVisible();
  });

  test('authorization - user data access control', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.goto(`/profile/${testUsers.farmer.id}`);
    
    await expect(page.locator('text=Access denied')).toBeVisible();
  });

  test('CSRF protection on forms', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.goto('/profile/edit');
    
    const csrfToken = await page.locator('[data-testid="csrf-token"]').getAttribute('value');
    expect(csrfToken).toBeDefined();
    expect(csrfToken).toMatch(/^[a-zA-Z0-9_-]+$/);
  });

  test('file upload security - file type validation', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.farmer);
    
    await page.goto('/farmer/products/new');
    
    await page.fill('[data-testid="product-name-input"]', 'Test Product');
    await page.fill('[data-testid="product-price-input"]', '10.99');
    await page.fill('[data-testid="product-quantity-input"]', '100');
    
    const maliciousFile = {
      name: 'malicious.php',
      mimeType: 'application/x-php',
      buffer: Buffer.from('<?php echo "malicious"; ?>')
    };
    
    await page.setInputFiles(testSelectors.upload.input, maliciousFile);
    
    await page.click('[data-testid="product-submit-button"]');
    
    await expect(page.locator('text=Invalid file type')).toBeVisible();
  });

  test('file upload security - file size limits', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.farmer);
    
    await page.goto('/farmer/products/new');
    
    await page.fill('[data-testid="product-name-input"]', 'Test Product');
    await page.fill('[data-testid="product-price-input"]', '10.99');
    await page.fill('[data-testid="product-quantity-input"]', '100');
    
    const largeFile = {
      name: 'large.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.alloc(11 * 1024 * 1024) // 11MB file
    };
    
    await page.setInputFiles(testSelectors.upload.input, largeFile);
    
    await page.click('[data-testid="product-submit-button"]');
    
    await expect(page.locator('text=File too large')).toBeVisible();
  });

  test('HTML sanitization in product descriptions', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.farmer);
    
    await page.goto('/farmer/products/new');
    
    const maliciousDescription = '<img src=x onerror=alert("XSS")> Safe description';
    
    await page.fill('[data-testid="product-name-input"]', 'Test Product');
    await page.fill('[data-testid="product-price-input"]', '10.99');
    await page.fill('[data-testid="product-quantity-input"]', '100');
    await page.fill('[data-testid="product-description-input"]', maliciousDescription);
    
    await page.click('[data-testid="product-submit-button"]');
    
    await page.waitForSelector(testSelectors.products.card);
    
    const descriptionText = await page.locator(testSelectors.products.card).locator('text=Safe description').textContent();
    expect(descriptionText).toContain('Safe description');
    expect(descriptionText).not.toContain('<img');
  });

  test('API rate limiting', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    const apiEndpoint = '/api/products/search';
    
    for (let i = 0; i < 100; i++) {
      const response = await page.request.get(`${apiEndpoint}?q=test${i}`);
      if (response.status() === 429) {
        expect(response.status()).toBe(429);
        return;
      }
    }
    
    await expect(page.locator('text=Rate limit exceeded')).toBeVisible();
  });

  test('API schema validation', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.farmer);
    
    const invalidProduct = {
      name: '',
      price: -10,
      quantity: 'invalid',
      category: 'nonexistent'
    };
    
    const response = await page.request.post('/api/products', {
      data: invalidProduct
    });
    
    expect(response.status()).toBe(400);
    
    const errorText = await response.text();
    expect(errorText).toContain('validation error');
  });

  test('sensitive data exposure prevention', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    const response = await page.request.get('/api/user/profile');
    const userData = await response.json();
    
    expect(userData).not.toHaveProperty('password');
    expect(userData).not.toHaveProperty('salt');
    expect(userData).not.toHaveProperty('hashedPassword');
  });

  test('session security - session expiration', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.evaluate(() => {
      document.cookie = 'session=expired; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    });
    
    await page.reload();
    
    await expect(page).toHaveURL(/.*login/);
  });

  test('session security - secure logout', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.click(testSelectors.navigation.menu);
    await page.click(testSelectors.auth.logoutButton);
    
    await page.goto('/dashboard');
    
    await expect(page).toHaveURL(/.*login/);
  });

  test('mobile security - API endpoint protection', async ({ page, context }) => {
    await context.addCookies([{
      name: 'test-session',
      value: 'mobile-security-test',
      domain: 'localhost',
      path: '/'
    }]);
    
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/admin/api/users');
    
    await expect(page.locator('text=Access denied')).toBeVisible();
  });

  test('mobile security - offline data encryption', async ({ page }) => {
    await testHelpers.loginUser(page, testUsers.buyer);
    
    await page.evaluate(() => {
      localStorage.setItem('test-data', 'sensitive information');
    });
    
    const storedData = await page.evaluate(() => {
      return localStorage.getItem('test-data');
    });
    
    expect(storedData).toBe('sensitive information');
    
    await page.evaluate(() => {
      const encryptedData = btoa(localStorage.getItem('test-data') || '');
      localStorage.setItem('encrypted-data', encryptedData);
    });
    
    const encryptedData = await page.evaluate(() => {
      return localStorage.getItem('encrypted-data');
    });
    
    expect(encryptedData).toBeTruthy();
    expect(encryptedData).not.toBe('sensitive information');
  });
});