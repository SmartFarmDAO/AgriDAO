import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import LoginForm from '../components/auth/LoginForm';

describe('AgriDAO Frontend Tests', () => {
  test('renders app without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
  });
  
  test('login form renders correctly', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
  
  test('navigation works', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    // Add navigation tests
  });
});
