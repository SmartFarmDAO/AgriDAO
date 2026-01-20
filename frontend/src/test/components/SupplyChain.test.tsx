import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../utils/test-utils';
import SupplyChain from '../../pages/SupplyChain';

// Mock translation
vi.mock('@/i18n/config', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

describe('SupplyChain', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders without crashing when API returns non-array', async () => {
    // Mock global fetch
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ error: 'Some error' }), // Non-array response
    } as Response);

    render(<SupplyChain />);

    // Should see the title (key from translation)
    expect(screen.getByText('supplyChain.title')).toBeInTheDocument();
    
    // Should see "No active shipments" fallback
    await waitFor(() => {
      expect(screen.getByText('No active shipments')).toBeInTheDocument();
    });
  });

  it('renders active shipments when API returns array', async () => {
     global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ([{
          id: 1,
          name: 'Test Asset',
          origin: 'Origin',
          current_location: 'Location',
          created_at: new Date().toISOString(),
          carrier: 'dhl',
          status: 'In Transit',
          tracking_number: '123'
      }]),
    } as Response);

    render(<SupplyChain />);

    await waitFor(() => {
        expect(screen.getByText('Test Asset')).toBeInTheDocument();
    });
  });
});
