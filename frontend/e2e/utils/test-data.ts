export interface TestUser {
  email: string;
  password: string;
  name: string;
  role: 'farmer' | 'buyer';
  phone?: string;
  address?: string;
}

export interface TestProduct {
  name: string;
  description: string;
  price: number;
  quantity: number;
  category: string;
  images: string[];
}

export interface TestOrder {
  items: Array<{
    productId: string;
    quantity: number;
    price: number;
  }>;
  shippingAddress: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
  };
  paymentMethod: 'card' | 'bank_transfer';
}

export const generateTestUser = (): TestUser => ({
  email: `test-${Date.now()}@example.com`,
  password: 'TestPass123!',
  name: `Test User ${Date.now()}`,
  role: Math.random() > 0.5 ? 'farmer' : 'buyer',
  phone: `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`,
  address: '123 Test Street, Test City, TC 12345'
});

export const generateTestProduct = (): TestProduct => ({
  name: `Test Product ${Date.now()}`,
  description: 'This is a test product for E2E testing',
  price: Math.floor(Math.random() * 1000) + 10,
  quantity: Math.floor(Math.random() * 100) + 1,
  category: ['vegetables', 'fruits', 'grains', 'dairy'][Math.floor(Math.random() * 4)],
  images: ['https://via.placeholder.com/300x200']
});

export const generateTestOrder = (productId: string): TestOrder => ({
  items: [{
    productId,
    quantity: Math.floor(Math.random() * 5) + 1,
    price: Math.floor(Math.random() * 100) + 10
  }],
  shippingAddress: {
    street: '123 Test Street',
    city: 'Test City',
    state: 'Test State',
    zipCode: '12345'
  },
  paymentMethod: 'card'
});

export const testUsers = {
  farmer: {
    email: 'farmer@test.com',
    password: 'FarmerPass123!',
    name: 'Test Farmer',
    role: 'farmer' as const,
    phone: '+1234567890',
    address: '456 Farm Road, Rural Town, RT 67890'
  },
  buyer: {
    email: 'buyer@test.com',
    password: 'BuyerPass123!',
    name: 'Test Buyer',
    role: 'buyer' as const,
    phone: '+1987654321',
    address: '789 Market Street, City Center, CC 54321'
  },
  admin: {
    email: 'admin@test.com',
    password: 'AdminPass123!',
    name: 'Test Admin',
    role: 'buyer' as const,
    phone: '+1112223333',
    address: '100 Admin Avenue, Admin City, AC 11111'
  },
  newUser: {
    email: 'newuser@test.com',
    password: 'NewUserPass123!',
    name: 'New Test User',
    role: 'buyer' as const,
    phone: '+1555666777',
    address: '321 New Street, New City, NC 33333'
  }
};

export const testProducts = {
  organicTomatoes: {
    name: 'Organic Tomatoes',
    description: 'Fresh organic tomatoes from local farm',
    price: 2.99,
    quantity: 50,
    category: 'vegetables',
    images: ['https://via.placeholder.com/300x200/FF6347/FFFFFF?text=Tomatoes']
  },
  freshApples: {
    name: 'Fresh Apples',
    description: 'Crisp and sweet apples from the orchard',
    price: 3.49,
    quantity: 100,
    category: 'fruits',
    images: ['https://via.placeholder.com/300x200/8B4513/FFFFFF?text=Apples']
  },
  wholeWheatFlour: {
    name: 'Whole Wheat Flour',
    description: 'Stone-ground whole wheat flour',
    price: 4.99,
    quantity: 25,
    category: 'grains',
    images: ['https://via.placeholder.com/300x200/F5DEB3/000000?text=Flour']
  }
};

export const testOrders = {
  sampleOrder: {
    items: [{
      productId: 'test-product-1',
      quantity: 2,
      price: 25.99
    }],
    shippingAddress: {
      street: '123 Test Street',
      city: 'Test City',
      state: 'Test State',
      zipCode: '12345'
    },
    paymentMethod: 'card' as const
  }
};

export const apiEndpoints = {
  auth: {
    register: '/api/auth/register',
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    refresh: '/api/auth/refresh',
    profile: '/api/users/profile'
  },
  products: {
    list: '/api/products',
    create: '/api/products',
    get: (id: string) => `/api/products/${id}`,
    update: (id: string) => `/api/products/${id}`,
    delete: (id: string) => `/api/products/${id}`,
    search: '/api/products/search',
    byFarmer: (farmerId: string) => `/api/products/farmer/${farmerId}`
  },
  orders: {
    list: '/api/orders',
    create: '/api/orders',
    get: (id: string) => `/api/orders/${id}`,
    update: (id: string) => `/api/orders/${id}`,
    cancel: (id: string) => `/api/orders/${id}/cancel`,
    track: (id: string) => `/api/orders/${id}/track`
  },
  bids: {
    list: '/api/bids',
    create: '/api/bids',
    get: (id: string) => `/api/bids/${id}`,
    accept: (id: string) => `/api/bids/${id}/accept`,
    reject: (id: string) => `/api/bids/${id}/reject`
  },
  cart: {
    get: '/api/cart',
    add: '/api/cart/add',
    remove: '/api/cart/remove',
    update: '/api/cart/update',
    clear: '/api/cart/clear'
  }
};

export const testSelectors = {
  auth: {
    loginForm: '[data-testid="login-form"]',
    registerForm: '[data-testid="register-form"]',
    emailInput: '[data-testid="email-input"]',
    passwordInput: '[data-testid="password-input"]',
    confirmPasswordInput: '[data-testid="confirm-password-input"]',
    submitButton: '[data-testid="submit-button"]',
    errorMessage: '[data-testid="error-message"]',
    successMessage: '[data-testid="success-message"]',
    logoutButton: '[data-testid="logout-button"]',
  },
  navigation: {
    menu: '[data-testid="navigation-menu"]',
    dashboard: '[data-testid="nav-dashboard"]',
    products: '[data-testid="nav-products"]',
    orders: '[data-testid="nav-orders"]',
    profile: '[data-testid="nav-profile"]',
    cart: '[data-testid="nav-cart"]',
    logout: '[data-testid="nav-logout"]',
  },
  products: {
    list: '[data-testid="product-list"]',
    card: '[data-testid="product-card"]',
    search: '[data-testid="product-search"]',
    filter: '[data-testid="product-filter"]',
    addToCart: '[data-testid="add-to-cart"]',
    image: '[data-testid="product-image"]',
    price: '[data-testid="product-price"]',
    name: '[data-testid="product-name"]',
  },
  cart: {
    container: '[data-testid="cart-container"]',
    items: '[data-testid="cart-items"]',
    total: '[data-testid="cart-total"]',
    checkout: '[data-testid="checkout-button"]',
    quantity: '[data-testid="cart-quantity"]',
    remove: '[data-testid="remove-from-cart"]',
  },
  orders: {
    list: '[data-testid="order-list"]',
    status: '[data-testid="order-status"]',
    tracking: '[data-testid="order-tracking"]',
    details: '[data-testid="order-details"]',
  },
  profile: {
    avatar: '[data-testid="profile-avatar"]',
    name: '[data-testid="profile-name"]',
    email: '[data-testid="profile-email"]',
    edit: '[data-testid="profile-edit"]',
    save: '[data-testid="profile-save"]',
  },
  upload: {
    input: '[data-testid="file-input"]',
    preview: '[data-testid="file-preview"]',
    submit: '[data-testid="upload-submit"]',
    progress: '[data-testid="upload-progress"]',
  },
  mobile: {
    menuButton: '[data-testid="mobile-menu-button"]',
    sidebar: '[data-testid="mobile-sidebar"]',
    swipeArea: '[data-testid="mobile-swipe-area"]',
    touchTarget: '[data-testid="mobile-touch-target"]',
  },
  offline: {
    status: '[data-testid="offline-status"]',
    syncButton: '[data-testid="sync-button"]',
    pendingCount: '[data-testid="pending-count"]',
  },
};

export const testHelpers = {
  async createUser(page: any, user: TestUser) {
    await page.goto('/register');
    await page.fill(testSelectors.auth.emailInput, user.email);
    await page.fill(testSelectors.auth.passwordInput, user.password);
    await page.fill(testSelectors.auth.confirmPasswordInput, user.password);
    await page.click(testSelectors.auth.submitButton);
    await page.waitForSelector(testSelectors.auth.successMessage);
  },

  async loginUser(page: any, user: TestUser) {
    await page.goto('/login');
    await page.fill(testSelectors.auth.emailInput, user.email);
    await page.fill(testSelectors.auth.passwordInput, user.password);
    await page.click(testSelectors.auth.submitButton);
    await page.waitForSelector(testSelectors.navigation.menu);
  },

  async createProduct(page: any, product: TestProduct) {
    await page.goto('/farmer/products/new');
    await page.fill('[data-testid="product-name-input"]', product.name);
    await page.fill('[data-testid="product-price-input"]', product.price.toString());
    await page.fill('[data-testid="product-quantity-input"]', product.quantity.toString());
    await page.selectOption('[data-testid="product-category-select"]', product.category);
    await page.fill('[data-testid="product-description-input"]', product.description);
    
    const fileInput = await page.locator(testSelectors.upload.input);
    await fileInput.setInputFiles(product.image);
    
    await page.click('[data-testid="product-submit-button"]');
    await page.waitForSelector(testSelectors.products.card);
  },

  async addToCart(page: any, productIndex = 0) {
    const addToCartButtons = await page.locator(testSelectors.products.addToCart);
    await addToCartButtons.nth(productIndex).click();
    await page.waitForSelector(testSelectors.cart.container);
  },

  async waitForNetworkIdle(page: any, timeout = 5000) {
    await page.waitForLoadState('networkidle', { timeout });
  },

  async waitForSelector(page: any, selector: string, timeout = 5000) {
    await page.waitForSelector(selector, { timeout });
  },

  async waitForText(page: any, text: string, timeout = 5000) {
    await page.waitForSelector(`text=${text}`, { timeout });
  },

  async clearCart(page: any) {
    await page.goto('/cart');
    const removeButtons = await page.locator(testSelectors.cart.remove);
    const count = await removeButtons.count();
    for (let i = 0; i < count; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(500);
    }
  },

  async checkOfflineStatus(page: any) {
    return await page.evaluate(() => {
      return !navigator.onLine;
    });
  },

  async simulateOffline(page: any) {
    await page.context().setOffline(true);
  },

  async simulateOnline(page: any) {
    await page.context().setOffline(false);
  },

  async waitForSync(page: any) {
    await page.waitForSelector(testSelectors.offline.syncButton);
    await page.click(testSelectors.offline.syncButton);
    await page.waitForSelector(testSelectors.offline.pendingCount, { state: 'hidden' });
  },
};