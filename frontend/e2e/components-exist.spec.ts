import { test, expect } from '@playwright/test';

test.describe('New Features - Component Existence', () => {
  test('Community component exists', async () => {
    const fs = require('fs');
    const path = require('path');
    
    const componentPath = path.join(__dirname, '../src/components/Community.tsx');
    expect(fs.existsSync(componentPath)).toBeTruthy();
  });

  test('SupplyChain component exists', async () => {
    const fs = require('fs');
    const path = require('path');
    
    const componentPath = path.join(__dirname, '../src/components/SupplyChain.tsx');
    expect(fs.existsSync(componentPath)).toBeTruthy();
  });

  test('Blockchain component exists', async () => {
    const fs = require('fs');
    const path = require('path');
    
    const componentPath = path.join(__dirname, '../src/components/Blockchain.tsx');
    expect(fs.existsSync(componentPath)).toBeTruthy();
  });

  test('Community page exists', async () => {
    const fs = require('fs');
    const path = require('path');
    
    const pagePath = path.join(__dirname, '../src/pages/Community.tsx');
    expect(fs.existsSync(pagePath)).toBeTruthy();
  });

  test('Blockchain page exists', async () => {
    const fs = require('fs');
    const path = require('path');
    
    const pagePath = path.join(__dirname, '../src/pages/BlockchainPage.tsx');
    expect(fs.existsSync(pagePath)).toBeTruthy();
  });
});
