---
inclusion: always
---

# My Global Conventions

## Rules for AI Assistants

### Standard Development Workflow

1. Always update the appropriate README or the appropriate design document when you make a change that impacts the contents of these documents.
2. Do not create additional markdown files in the repository unless you are instructed explicitly to.
3. As you make changes, you must commit them grouped by single logical purpose, typically under 150 lines of source code plus 150 lines of test code. For larger changes, break them into multiple commits that each follow this principle.
4. Commit your changes in git using a well-formed commit message consisting of a single sentence summary and no more than a few paragraphs explaining the change and your testing. After this explanation, place the prompt the user used to trigger this work prefixed with a "Prompt: " after a single line consisting of '───'. Make sure there are no empty lines before or after this line. Word wrap all paragraphs at 72 columns including the prompt. For the author of the commit, use the configured username in git with ' (Kiro)' appended and the user email. For example, `git commit --author="John Doe (Kiro) <john@bigco.com>"`
5. Avoid unit tests that test too much, prefer tests that test small piece of functionality.

**ALWAYS FOLLOW THESE RULES WHEN YOU WORK IN THIS PROJECT**

## Code Style

- Use descriptive variable names
- Prefer functional programming patterns
- Always include error handling
- 2-space indentation for JS/TS, 4-space for Python
- Trailing commas in multi-line arrays/objects
- camelCase for functions and variables
- PascalCase for components and classes
- SCREAMING_SNAKE_CASE for constants

## Documentation

- Add comments for complex logic
- Keep README files updated
- JSDoc for all public functions
- Inline comments for complex logic only
- Include setup instructions in README

## Testing Standards

- Minimum 80% coverage for business logic
- Test files in `__tests__/` directories
- Use Jest + React Testing Library for JS/TS
- Arrange-Act-Assert pattern
- Descriptive test names (it should...)
- Mock external dependencies

## Security Essentials

- Never commit secrets (use environment variables)
- Validate all user inputs
- Sanitize data before SQL/HTML rendering
- Use parameterized queries, never string concatenation
- HTTPS only, no mixed content
- Implement rate limiting on APIs

## Git Conventions

- Follow Conventional Commits format
- Types: feat, fix, docs, refactor, test, chore
- Format: `type(scope): description`
- Example: `feat(auth): add OAuth2 support`
- Branch naming: `feature/xxx`, `fix/xxx`

## Architecture Principles

- Separation of concerns
- DRY but not at the cost of clarity
- Composition over inheritance
- Fail fast with descriptive errors
- Single Responsibility Principle

## What NOT to Include in Code

- API keys or secrets (use environment variables)
- Database credentials
- Internal URLs or endpoints
- Customer data or PII
- Hardcoded passwords or tokens
