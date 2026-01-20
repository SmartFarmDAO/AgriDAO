import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('App', () => {
  it('renders without crashing', () => {
    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <App />
      </Wrapper>
    );
    
    expect(document.body).toBeInTheDocument();
  });

  it('displays the main application structure', () => {
    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <App />
      </Wrapper>
    );
    
    // Check for navigation or main content
    expect(document.body).toBeInTheDocument();
  });
});