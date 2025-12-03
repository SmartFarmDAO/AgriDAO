# Contributing to AgriDAO

Thank you for your interest in contributing to AgriDAO! This document provides guidelines and instructions for contributing to the project.

Thank you for your interest in contributing to AgriDAO! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose

### Setup Development Environment

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/AgriDAO.git
cd AgriDAO
```

2. **Install dependencies**
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your configuration

# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

4. **Start development servers**
```bash
# Frontend (from frontend directory)
npm run dev

# Backend (from project root)
cd backend
docker-compose up --build
```

## 🔄 Development Workflow

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

Example: `feature/user-authentication`, `fix/cart-calculation`

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(auth): add two-factor authentication

Implement 2FA using TOTP for enhanced security.
Users can enable 2FA in their profile settings.

Closes #123
```

## 📝 Coding Standards

### TypeScript/JavaScript (Frontend)

- Use TypeScript strict mode
- Follow ESLint configuration
- Use Prettier for formatting
- Prefer functional components with hooks
- Use meaningful variable and function names
- Add JSDoc comments for complex functions

```typescript
/**
 * Calculates the total price of items in the cart
 * @param items - Array of cart items
 * @returns Total price including tax
 */
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}
```

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Add docstrings for functions and classes
- Use meaningful variable names
- Keep functions focused and small

```python
def calculate_order_total(items: List[OrderItem]) -> Decimal:
    """
    Calculate the total price for an order.
    
    Args:
        items: List of order items
        
    Returns:
        Total price as Decimal
    """
    return sum(item.price * item.quantity for item in items)
```

### File Organization

- Keep files focused on a single responsibility
- Group related functionality
- Use index files for clean imports
- Follow the project structure (see [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md))

## 🧪 Testing Requirements

### Frontend Testing

All new features must include:

1. **Unit Tests** (Vitest)
```typescript
import { describe, it, expect } from 'vitest';
import { calculateTotal } from './cart';

describe('calculateTotal', () => {
  it('should calculate total correctly', () => {
    const items = [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 3 }
    ];
    expect(calculateTotal(items)).toBe(35);
  });
});
```

2. **Component Tests** (React Testing Library)
```typescript
import { render, screen } from '@testing-library/react';
import { CartItem } from './CartItem';

test('renders cart item', () => {
  render(<CartItem name="Apple" price={1.99} />);
  expect(screen.getByText('Apple')).toBeInTheDocument();
});
```

3. **E2E Tests** (Playwright) for critical flows
```typescript
test('user can add item to cart', async ({ page }) => {
  await page.goto('/marketplace');
  await page.click('[data-testid="add-to-cart"]');
  await expect(page.locator('.cart-count')).toHaveText('1');
});
```

### Backend Testing

All new features must include:

1. **Unit Tests** (pytest)
```python
def test_calculate_order_total():
    items = [
        OrderItem(price=Decimal('10.00'), quantity=2),
        OrderItem(price=Decimal('5.00'), quantity=3)
    ]
    assert calculate_order_total(items) == Decimal('35.00')
```

2. **Integration Tests** for API endpoints
```python
def test_create_order(client):
    response = client.post('/api/orders', json={
        'items': [{'product_id': 1, 'quantity': 2}]
    })
    assert response.status_code == 201
```

### Running Tests

```bash
# Frontend tests
cd frontend
npm test                    # Unit tests
npm run test:coverage       # With coverage
npm run test:e2e           # E2E tests

# Backend tests
cd backend
pytest                      # All tests
pytest --cov               # With coverage
```

### Test Coverage Requirements

- Minimum 80% code coverage for new code
- 100% coverage for critical business logic
- All edge cases must be tested

## 📚 Documentation

### Code Documentation

- Add JSDoc/docstrings for all public functions
- Document complex algorithms
- Explain non-obvious code decisions
- Update README when adding features

### User Documentation

When adding user-facing features:

1. Update relevant guides in `docs/guides/`
2. Add API documentation in `docs/api/`
3. Update troubleshooting if applicable
4. Add examples and screenshots

### Documentation Structure

Place documentation in appropriate folders:
- `docs/guides/` - User guides and tutorials
- `docs/architecture/` - System architecture
- `docs/deployment/` - Deployment instructions
- `docs/troubleshooting/` - Problem resolution
- `docs/api/` - API documentation

## 🔍 Pull Request Process

### Before Submitting

1. **Update your branch**
```bash
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main
```

2. **Run all tests**
```bash
# Frontend
cd frontend
npm run lint
npm run typecheck
npm test
npm run test:e2e

# Backend
cd backend
pytest
```

3. **Update documentation**
- Update relevant docs
- Add/update tests
- Update CHANGELOG if applicable

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] PR description is clear and complete

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed
```

### Review Process

1. Submit PR with clear description
2. Address reviewer feedback
3. Ensure CI/CD passes
4. Get approval from maintainers
5. Squash and merge

## 🏗️ Project Structure

Familiarize yourself with the project structure:

```
AgriDAO/
├── frontend/          # React frontend
├── backend/           # FastAPI backend
├── mobile/            # React Native mobile
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for detailed structure.

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., macOS]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution**
How you'd like it to work

**Describe alternatives**
Alternative solutions considered

**Additional context**
Mockups, examples, etc.
```

## 🔒 Security

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Follow security best practices
- Report security issues privately to security@agridao.com

## 📞 Getting Help

- Check [Documentation](./docs/INDEX.md)
- Review [Troubleshooting](./docs/troubleshooting/)
- Ask in GitHub Discussions
- Join our Discord community

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to AgriDAO! 🌾
