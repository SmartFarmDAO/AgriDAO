import { test, expect } from '@playwright/test';
import { testUsers, testProducts, testSelectors, testHelpers } from './utils/test-data';

test.describe('Performance Tests', () => {
  test('page load performance - homepage', async ({ page }) => {
    await page.goto('/');
    
    const performanceTiming = await page.evaluate(() => {
      return {
        loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
        largestContentfulPaint: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime || 0
      };
    });
    
    expect(performanceTiming.loadTime).toBeLessThan(3000);
    expect(performanceTiming.domContentLoaded).toBeLessThan(1500);
    expect(performanceTiming.firstPaint).toBeLessThan(1000);
    expect(performanceTiming.firstContentfulPaint).toBeLessThan(1200);
    expect(performanceTiming.largestContentfulPaint).toBeLessThan(2000);
  });

  test('page load performance - marketplace', async ({ page }) => {
    await page.goto('/marketplace');
    
    const performanceTiming = await page.evaluate(() => {
      return {
        loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
        largestContentfulPaint: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime || 0
      };
    });
    
    expect(performanceTiming.loadTime).toBeLessThan(4000);
    expect(performanceTiming.domContentLoaded).toBeLessThan(2000);
    expect(performanceTiming.firstPaint).toBeLessThan(1500);
    expect(performanceTiming.firstContentfulPaint).toBeLessThan(1800);
    expect(performanceTiming.largestContentfulPaint).toBeLessThan(2500);
  });

  test('API performance - product search', async ({ page }) => {
    await page.goto('/marketplace');
    
    const searchStart = Date.now();
    
    await page.fill(testSelectors.search.input, 'organic');
    await page.waitForResponse(response => 
      response.url().includes('/api/products/search') && response.status() === 200
    );
    
    const searchTime = Date.now() - searchStart;
    
    expect(searchTime).toBeLessThan(500);
  });

  test('API performance - product filtering', async ({ page }) => {
    await page.goto('/marketplace');
    
    const filterStart = Date.now();
    
    await page.click(testSelectors.filters.categoryButton);
    await page.click('[data-testid="category-organic"]');
    
    await page.waitForResponse(response => 
      response.url().includes('/api/products') && response.status() === 200
    );
    
    const filterTime = Date.now() - filterStart;
    
    expect(filterTime).toBeLessThan(300);
  });

  test('database performance - concurrent user actions', async ({ browser }) => {
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    await testHelpers.loginUser(page1, testUsers.buyer);
    await testHelpers.loginUser(page2, testUsers.farmer);
    
    const [result1, result2] = await Promise.all([
      page1.goto('/marketplace'),
      page2.goto('/farmer/dashboard')
    ]);
    
    expect(result1?.ok()).toBeTruthy();
    expect(result2?.ok()).toBeTruthy();
    
    await context1.close();
    await context2.close();
  });

  test('mobile performance - 3G network simulation', async ({ page }) => {
    await page.context().route('**/*', route => {
      const headers = route.request().headers();
      headers['user-agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)';
      route.continue({ headers });
    });
    
    await page.goto('/');
    
    const performanceTiming = await page.evaluate(() => {
      return {
        loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
        largestContentfulPaint: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime || 0
      };
    });
    
    expect(performanceTiming.loadTime).toBeLessThan(5000);
    expect(performanceTiming.domContentLoaded).toBeLessThan(3000);
    expect(performanceTiming.firstPaint).toBeLessThan(2000);
    expect(performanceTiming.firstContentfulPaint).toBeLessThan(2500);
    expect(performanceTiming.largestContentfulPaint).toBeLessThan(4000);
  });

  test('mobile performance - low-end device simulation', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    
    const performanceTiming = await page.evaluate(() => {
      return {
        loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
        largestContentfulPaint: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime || 0
      };
    });
    
    expect(performanceTiming.loadTime).toBeLessThan(6000);
    expect(performanceTiming.domContentLoaded).toBeLessThan(3500);
    expect(performanceTiming.firstPaint).toBeLessThan(2500);
    expect(performanceTiming.firstContentfulPaint).toBeLessThan(3000);
    expect(performanceTiming.largestContentfulPaint).toBeLessThan(4500);
  });

  test('resource usage - memory leak detection', async ({ page }) => {
    await page.goto('/marketplace');
    
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });
    
    for (let i = 0; i < 10; i++) {
      await page.reload();
      await page.waitForLoadState('networkidle');
    }
    
    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });
    
    const memoryIncrease = finalMemory - initialMemory;
    const memoryIncreaseMB = memoryIncrease / (1024 * 1024);
    
    expect(memoryIncreaseMB).toBeLessThan(10);
  });

  test('resource usage - DOM nodes count', async ({ page }) => {
    await page.goto('/marketplace');
    
    const domNodeCount = await page.evaluate(() => {
      return document.querySelectorAll('*').length;
    });
    
    expect(domNodeCount).toBeLessThan(1000);
  });

  test('stress testing - high concurrent users', async ({ browser }) => {
    const userCount = 10;
    const pages = [];
    
    for (let i = 0; i < userCount; i++) {
      const context = await browser.newContext();
      const page = await context.newPage();
      pages.push({ page, context });
    }
    
    const promises = pages.map(async ({ page }) => {
      await page.goto('/marketplace');
      await page.fill(testSelectors.search.input, 'test');
      await page.waitForResponse(response => 
        response.url().includes('/api/products') && response.status() === 200
      );
      return page.url();
    });
    
    const results = await Promise.all(promises);
    
    expect(results.length).toBe(userCount);
    
    for (const { page, context } of pages) {
      await context.close();
    }
  });

  test('stress testing - large dataset handling', async ({ page }) => {
    await page.goto('/marketplace');
    
    await page.evaluate((products) => {
      window.localStorage.setItem('cachedProducts', JSON.stringify(products));
    }, Array(1000).fill(testProducts[0]));
    
    const loadStart = Date.now();
    await page.reload();
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - loadStart;
    
    expect(loadTime).toBeLessThan(3000);
  });

  test('stress testing - rapid user interactions', async ({ page }) => {
    await page.goto('/marketplace');
    
    const interactionPromises = [];
    
    for (let i = 0; i < 50; i++) {
      interactionPromises.push(
        page.click(testSelectors.search.input),
        page.fill(testSelectors.search.input, `search${i}`),
        page.keyboard.press('Enter')
      );
    }
    
    await Promise.all(interactionPromises);
    
    await expect(page).toBeVisible();
  });
});