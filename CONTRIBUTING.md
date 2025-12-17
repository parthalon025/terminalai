# Contributing to TerminalAI

Thank you for your interest in contributing to TerminalAI! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Node.js 20.x or higher
- pnpm 8.x or higher
- Git

### Development Setup

1. **Fork the repository**

   Click the "Fork" button on GitHub to create your own copy.

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/terminalai.git
   cd terminalai
   ```

3. **Install dependencies**

   ```bash
   pnpm install
   ```

4. **Set up Git hooks**

   ```bash
   pnpm prepare
   ```

5. **Verify setup**

   ```bash
   pnpm test
   pnpm lint
   pnpm build
   ```

## Development Workflow

### Branch Naming

Use descriptive branch names following this pattern:

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions/modifications
- `chore/description` - Maintenance tasks

### Running the Development Server

```bash
pnpm dev
```

### Running Tests

```bash
# Run all tests
pnpm test

# Run unit tests only
pnpm test:unit

# Run integration tests
pnpm test:integration

# Run E2E tests
pnpm test:e2e

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm test:watch
```

### Linting and Formatting

```bash
# Run ESLint
pnpm lint

# Fix ESLint issues
pnpm lint:fix

# Check formatting
pnpm format:check

# Fix formatting
pnpm format

# Type check
pnpm type-check
```

## Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

   - Write clean, maintainable code
   - Add tests for new functionality
   - Update documentation as needed

3. **Ensure quality checks pass**

   ```bash
   pnpm lint
   pnpm type-check
   pnpm test
   pnpm build
   ```

4. **Commit your changes**

   Follow our [commit message guidelines](#commit-messages).

5. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**

   - Fill out the PR template completely
   - Link any related issues
   - Request reviews from maintainers

7. **Address feedback**

   - Respond to all review comments
   - Make requested changes promptly
   - Re-request reviews after changes

## Coding Standards

### TypeScript

- Use strict TypeScript (`strict: true`)
- Avoid `any` type - use proper typing or `unknown`
- Export types alongside implementations
- Use interfaces for object shapes, types for unions/intersections

### Style Guide

- Use 2 spaces for indentation
- Use single quotes for strings
- Always use semicolons
- Maximum line length: 100 characters
- Use trailing commas in multi-line structures

### File Organization

```
src/
├── cli/           # CLI entry points and commands
├── core/          # Core business logic
├── ai/            # AI integration modules
├── config/        # Configuration management
├── utils/         # Utility functions
└── types/         # TypeScript type definitions
```

### Naming Conventions

- **Files**: `kebab-case.ts` (e.g., `command-parser.ts`)
- **Classes**: `PascalCase` (e.g., `CommandParser`)
- **Functions**: `camelCase` (e.g., `parseCommand`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Interfaces**: `PascalCase` with descriptive names (e.g., `CommandConfig`)
- **Types**: `PascalCase` (e.g., `CommandType`)

## Testing Guidelines

### Test Structure

```typescript
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should do something specific', () => {
      // Arrange
      const input = 'test';

      // Act
      const result = doSomething(input);

      // Assert
      expect(result).toBe('expected');
    });
  });
});
```

### What to Test

- All public methods and functions
- Edge cases and error conditions
- Integration between components
- User-facing workflows (E2E)

### Coverage Requirements

- Unit tests: 80% minimum coverage
- Critical paths: 100% coverage
- Integration tests for all external interactions

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/modifications
- `build`: Build system changes
- `ci`: CI configuration changes
- `chore`: Maintenance tasks

### Examples

```bash
feat(cli): add interactive mode for queries
fix(ai): handle rate limiting errors gracefully
docs(readme): update installation instructions
test(parser): add edge case tests for empty input
```

## Questions?

If you have questions or need help:

1. Check existing [issues](https://github.com/parthalon025/terminalai/issues) and [discussions](https://github.com/parthalon025/terminalai/discussions)
2. Open a new discussion for general questions
3. Open an issue for bugs or feature requests

Thank you for contributing!
