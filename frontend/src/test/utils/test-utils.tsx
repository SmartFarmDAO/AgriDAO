import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';

// Mock auth provider
const MockAuthProvider = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

// Mock wallet provider
const MockWalletProvider = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

// Mock config provider
const MockConfigProvider = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

interface AllTheProvidersProps {
  children: React.ReactNode;
}

const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <TooltipProvider>
          <MockWalletProvider>
            <MockAuthProvider>
              <MockConfigProvider>
                <Toaster />
                {children}
              </MockConfigProvider>
            </MockAuthProvider>
          </MockWalletProvider>
        </TooltipProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

// Utility functions for testing
export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  role: 'buyer',
  status: 'active',
  created_at: '2023-01-01T00:00:00Z',
  ...overrides,
});

export const createMockProduct = (overrides = {}) => ({
  id: 1,
  name: 'Test Product',
  description: 'Test product description',
  price: 10.99,
  category: 'vegetables',
  farmer_id: 1,
  quantity_available: 100,
  unit: 'lb',
  status: 'active',
  created_at: '2023-01-01T00:00:00Z',
  ...overrides,
});

export const createMockOrder = (overrides = {}) => ({
  id: 1,
  buyer_id: 1,
  status: 'pending',
  subtotal: 21.98,
  platform_fee: 2.20,
  total: 24.18,
  payment_status: 'unpaid',
  created_at: '2023-01-01T00:00:00Z',
  ...overrides,
});

export const waitForLoadingToFinish = () =>
  new Promise((resolve) => setTimeout(resolve, 0));

// Mock API responses
export const mockApiResponse = (data: any) => ({
  data,
  status: 200,
  statusText: 'OK',
  headers: {},
  config: {},
});

// Testing hooks utility
export const renderHook = (hook: () => any) => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AllTheProviders>{children}</AllTheProviders>
  );
  
  const TestComponent = () => {
    const hookResult = hook();
    return <div data-testid="hook-result">{JSON.stringify(hookResult)}</div>;
  };

  return render(<TestComponent />, { wrapper });
};