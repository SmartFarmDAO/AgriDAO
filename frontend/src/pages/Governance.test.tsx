import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import Governance from './Governance';
import * as api from '@/lib/api';
import { Proposal } from '@/types';

// Mock the api module
vi.mock('@/lib/api');

const mockProposals: Proposal[] = [
  {
    id: 1,
    title: 'Test Proposal 1',
    description: 'This is a test proposal.',
    status: 'open',
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    title: 'Test Proposal 2',
    description: 'Another test proposal.',
    status: 'passed',
    created_at: new Date().toISOString(),
  },
];

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderComponent = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Governance />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Governance Page', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.resetAllMocks();
  });

  it('should render proposals when data is fetched successfully', async () => {
    // Arrange
    (api.listProposals as vi.Mock).mockResolvedValue(mockProposals);

    // Act
    renderComponent();

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Test Proposal 1')).toBeInTheDocument();
      expect(screen.getByText('Test Proposal 2')).toBeInTheDocument();
    });
  });

  it('should display an error message when fetching proposals fails', async () => {
    // Arrange
    (api.listProposals as vi.Mock).mockRejectedValue(new Error('Failed to fetch'));

    // Act
    renderComponent();

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Error fetching proposals.')).toBeInTheDocument();
    });
  });

  it('should render the governance page structure', () => {
    // Arrange
    (api.listProposals as vi.Mock).mockResolvedValue([]);

    // Act
    renderComponent();

    // Assert
    expect(screen.getByText('Governance')).toBeInTheDocument();
    expect(screen.getByText('Create Proposal')).toBeInTheDocument();
  });
});
