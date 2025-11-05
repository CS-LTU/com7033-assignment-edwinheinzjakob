# Contributing Guidelines

Thank you for your interest in contributing to the Secure Stroke Prediction Dataset Management System!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/com7033-assignment-XXXX.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Install development dependencies: `pip install pytest pytest-cov black flake8 isort bandit`
7. Create a branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Code Style

We use the following tools for code quality:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **bandit**: Security linting

Before committing, run:
```bash
black app/ tests/
isort app/ tests/
flake8 app/ tests/
bandit -r app/
```

### Testing

Write tests for all new features and bug fixes.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py

# Run specific test
pytest tests/unit/test_security.py::TestEmailValidation::test_valid_emails
```

### Commit Messages

Use clear, descriptive commit messages following conventional commits:

```
feat: Add patient search functionality
fix: Fix password validation bug
docs: Update README with installation instructions
test: Add tests for authentication service
refactor: Refactor patient repository
```

### Pull Request Process

1. Ensure all tests pass: `pytest`
2. Ensure code coverage is maintained: `pytest --cov=app --cov-fail-under=90`
3. Update documentation if needed
4. Create a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots (if UI changes)
   - Test coverage information

## Code Structure

```
app/
├── blueprints/      # Flask blueprints
├── services/        # Business logic
├── repositories/    # Data access layer
├── security/        # Security utilities
├── schemas/         # Data validation schemas
├── utils/          # Utility functions
├── routes/          # Root routes
└── errors/         # Error handlers
```

## Writing Tests

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution (< 1 second)

### Integration Tests
- Test interaction between components
- Use test databases
- May take longer to execute

### E2E Tests
- Test complete user workflows
- Use test client
- May require external services (MongoDB)

## Security Considerations

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize output to prevent XSS
- Use parameterized queries
- Follow OWASP security guidelines

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation if API changes
- Add examples in docstrings

## Questions?

- Module Leader: x.lu@leedstrinity.ac.uk
- Assessment Team: assessment@leedstrinity.ac.uk

Thank you for contributing!

