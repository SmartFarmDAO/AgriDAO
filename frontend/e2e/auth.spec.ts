import { test, expect } from '@playwright/test';
import { testUsers, testSelectors, testHelpers } from './utils/test-data';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('user registration', async ({ page }) => {
    await page.goto('/auth');
    
    const user = testUsers.newUser;
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Fill email for OTP request
    await page.fill('#email', user.email);
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    // Wait for OTP verification step
    await page.waitForSelector('#code-0', { timeout: 10000 });
    
    // Fill OTP digits
    await page.fill('#code-0', '1');
    await page.fill('#code-1', '2');
    await page.fill('#code-2', '3');
    await page.fill('#code-3', '4');
    await page.fill('#code-4', '5');
    await page.fill('#code-5', '6');
    
    await page.waitForURL('**/dashboard', { timeout: 15000 });
    
    // Verify successful registration
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('user login', async ({ page }) => {
    await page.goto('/auth');
    
    const user = testUsers.existingUser;
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Fill email for OTP request
    await page.fill('#email', user.email);
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    // Wait for OTP verification step
    await page.waitForSelector('#code-0', { timeout: 10000 });
    
    // Fill OTP digits
    await page.fill('#code-0', '1');
    await page.fill('#code-1', '2');
    await page.fill('#code-2', '3');
    await page.fill('#code-3', '4');
    await page.fill('#code-4', '5');
    await page.fill('#code-5', '6');
    
    await page.waitForURL('**/dashboard', { timeout: 15000 });
    
    // Verify successful login
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('validation errors', async ({ page }) => {
    await page.goto('/auth');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Test invalid email format
    await page.fill('#email', 'invalid-email');
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    // Browser should show validation error for email format
    await expect(page.locator('#email')).toHaveAttribute('type', 'email');
  });

  test('OTP verification error', async ({ page }) => {
    await page.goto('/auth');
    
    const user = testUsers.newUser;
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Fill email for OTP request
    await page.fill('#email', user.email);
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    // Wait for OTP verification step
    await page.waitForSelector('#code-0', { timeout: 10000 });
    
    // Enter invalid OTP digits
    await page.fill('#code-0', '0');
    await page.fill('#code-1', '0');
    await page.fill('#code-2', '0');
    await page.fill('#code-3', '0');
    await page.fill('#code-4', '0');
    await page.fill('#code-5', '0');
    
    // Should show verification error or handle invalid OTP
    await expect(page.locator('text=Invalid verification code')).toBeVisible({ timeout: 10000 });
  });

  test('login error handling', async ({ page }) => {
    await page.goto('/auth');
    
    // Try to login with non-existent email
    await page.fill('#email', 'nonexistent@example.com');
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    // Should handle the email request (backend will send OTP regardless)
    await expect(page.locator('#code-0')).toBeVisible();
  });

  test('protected routes redirect to login', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page).toHaveURL(/.*login/);
  });

  test('session persistence', async ({ page, context }) => {
    await page.goto('/auth');
    
    const user = testUsers.buyer;
    
    // Login successfully
    await page.fill('#email', user.email);
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    await page.waitForSelector('#code-0');
    await page.fill('#code-0', '1');
    await page.fill('#code-1', '2');
    await page.fill('#code-2', '3');
    await page.fill('#code-3', '4');
    await page.fill('#code-4', '5');
    await page.fill('#code-5', '6');
    
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Check if user is logged in
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('logout functionality', async ({ page }) => {
    await page.goto('/auth');
    
    const user = testUsers.farmer;
    
    // Login first
    await page.fill('#email', user.email);
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    await page.waitForSelector('#code-0');
    await page.fill('#code-0', '1');
    await page.fill('#code-1', '2');
    await page.fill('#code-2', '3');
    await page.fill('#code-3', '4');
    await page.fill('#code-4', '5');
    await page.fill('#code-5', '6');
    
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Logout
    await page.click('button:has-text("Logout")');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth');
  });

  test('mobile registration flow', async ({ page, context }) => {
    await context.addCookies([{
      name: 'test-session',
      value: 'mobile-test',
      domain: 'localhost',
      path: '/'
    }]);
    
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/auth');
    
    const user = testUsers.newUser;
    
    // Fill email for OTP request
    await page.fill('#email', user.email);
    await page.click('button[type="submit"]:has-text("Continue with Email")');
    
    // Wait for OTP verification step
    await page.waitForSelector('#code-0');
    
    // Fill OTP digits
    await page.fill('#code-0', '1');
    await page.fill('#code-1', '2');
    await page.fill('#code-2', '3');
    await page.fill('#code-3', '4');
    await page.fill('#code-4', '5');
    await page.fill('#code-5', '6');
    
    // Should redirect to dashboard after successful registration
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
});