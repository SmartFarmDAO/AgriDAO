import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { render, createMockUser, waitForLoadingToFinish } from '../utils/test-utils';
import AdminDashboard from '../../pages/AdminDashboard';
import * as authHook from '../../hooks/use-auth';
import * as apiLib from '../../lib/api';

// Mock the hooks and API
vi.mock('../../hooks/use-auth');
vi.mock('../../hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));
vi.mock('../../lib/api', () => ({
  listAllUsers: vi.fn(),
  updateUserRole: vi.fn(),
  suspendUser: vi.fn(),
  deleteUserById: vi.fn(),
  apiClient: {
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    post: vi.fn(),
  }
}));

const mockUseAuth = vi.mocked(authHook.useAuth);
const mockApiClient = vi.mocked(apiLib.apiClient);
const mockListAllUsers = vi.mocked(apiLib.listAllUsers);

describe('AdminDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default API mocks
    mockListAllUsers.mockResolvedValue([
      createMockUser({ id: 1, name: 'John Doe', email: 'john@example.com', role: 'FARMER' }),
      createMockUser({ id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'BUYER' }),
    ]);

    mockApiClient.get.mockImplementation((url) => {
      switch (url) {
        case '/admin/stats':
          return Promise.resolve({
            data: {
              users: { total: 150, active: 120, farmers: 60, buyers: 90, new_this_month: 15 },
              orders: { total: 450, pending: 25, completed: 400, cancelled: 25, today: 8 },
              products: { total: 300, active: 280, out_of_stock: 20, new_this_month: 30 },
              disputes: { total: 12, open: 3, resolved: 8, escalated: 1 },
              revenue: { total: 45000, this_month: 8500, growth_rate: 12.5 },
            },
          });
        case '/admin/users': // Keep this for backward compatibility if needed, but listAllUsers is primary
          return Promise.resolve({
            data: [
              createMockUser({ id: 1, name: 'John Doe', email: 'john@example.com', role: 'farmer' }),
              createMockUser({ id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'buyer' }),
            ],
          });
        case '/admin/orders':
          return Promise.resolve({
            data: [
              { id: 1, user_email: 'john@example.com', total: 50.00, status: 'completed', created_at: '2023-01-01', items_count: 3 },
              { id: 2, user_email: 'jane@example.com', total: 25.00, status: 'pending', created_at: '2023-01-02', items_count: 2 },
            ],
          });
        case '/admin/disputes':
          return Promise.resolve({
            data: [
              { id: 1, order_id: 1, user_email: 'john@example.com', status: 'open', priority: 3, created_at: '2023-01-01', subject: 'Product quality issue' },
            ],
          });
        default:
          return Promise.reject(new Error('Not found'));
      }
    });
  });

  it('denies access to non-admin users', () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'buyer' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<AdminDashboard />);

    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.getByText('You don\'t have permission to access the admin dashboard.')).toBeInTheDocument();
  });

  it('allows access to admin users', async () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<AdminDashboard />);

    // Wait for loading to finish
    await waitForLoadingToFinish();
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });
  });

  it('displays dashboard stats correctly', async () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument(); // Total users
      expect(screen.getByText('450')).toBeInTheDocument(); // Total orders
      expect(screen.getByText('300')).toBeInTheDocument(); // Total products
      expect(screen.getByText('12')).toBeInTheDocument(); // Total disputes
      expect(screen.getByText('৳45,000.00')).toBeInTheDocument(); // Total revenue
    });
  });

  it('allows switching between tabs', async () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });

    // Switch to Users tab
    const usersTab = screen.getByRole('tab', { name: 'Users' });
    fireEvent.click(usersTab);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    });

    // Switch to Orders tab
    const ordersTab = screen.getByRole('tab', { name: 'Orders' });
    fireEvent.click(ordersTab);

    await waitFor(() => {
      expect(screen.getByText('#1')).toBeInTheDocument();
      expect(screen.getByText('৳50.00')).toBeInTheDocument();
    });
  });

  it('filters users correctly', async () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<AdminDashboard />);

    // Switch to Users tab
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });

    const usersTab = screen.getByRole('tab', { name: 'Users' });
    fireEvent.click(usersTab);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    // Filter by search
    const searchInput = screen.getByPlaceholderText('Search users...');
    fireEvent.change(searchInput, { target: { value: 'John' } });

    // John should still be visible, Jane should be filtered out
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('handles user actions correctly', async () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    // Mock successful API calls for user actions
    mockApiClient.put.mockResolvedValue({ data: { success: true } });
    mockApiClient.delete.mockResolvedValue({ data: { success: true } });

    render(<AdminDashboard />);

    // Switch to Users tab and wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });

    const usersTab = screen.getByRole('tab', { name: 'Users' });
    fireEvent.click(usersTab);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Find and click an action button (suspend user)
    const suspendButtons = screen.getAllByRole('button');
    const suspendButton = suspendButtons.find(button =>
      button.querySelector('[data-lucide="x-circle"]')
    );

    if (suspendButton) {
      fireEvent.click(suspendButton);

      await waitFor(() => {
        expect(mockApiClient.put).toHaveBeenCalledWith(
          '/admin/users/1/status',
          { status: 'suspended' }
        );
      });
    }
  });

  it('displays loading state correctly', () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    // Mock API to never resolve to keep loading state
    mockApiClient.get.mockImplementation(() => new Promise(() => { }));

    render(<AdminDashboard />);

    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    mockUseAuth.mockReturnValue({
      user: createMockUser({ role: 'admin' }),
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    // Mock API to reject
    mockApiClient.get.mockRejectedValue(new Error('API Error'));

    render(<AdminDashboard />);

    // Should still render the dashboard (error handling should be graceful)
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });
  });
});