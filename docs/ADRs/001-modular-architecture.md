# ADR 001: Modular Architecture

## Status
Accepted

## Context
The original application was built as a monolithic Flask app with all routes, business logic, and data access code in a single `app.py` file. This approach made the codebase difficult to maintain, test, and scale.

## Decision
We will refactor the application into a modular architecture using:
- **Blueprints** for route organization (auth, patients, dashboard, API)
- **Service Layer** for business logic separation
- **Repository Pattern** for data access abstraction
- **Application Factory Pattern** for flexible configuration

## Consequences

### Positive
- Improved code organization and maintainability
- Easier to test individual components
- Better separation of concerns
- Scalable architecture for future features
- Multiple developers can work on different modules simultaneously

### Negative
- More files to navigate
- Initial refactoring effort required
- Slightly more complex project structure

### Implementation
- Created `app/blueprints/` for route modules
- Created `app/services/` for business logic
- Created `app/repositories/` for data access
- Moved to application factory pattern in `app/__init__.py`

## References
- Flask Blueprints documentation
- Repository Pattern
- Service Layer Pattern

