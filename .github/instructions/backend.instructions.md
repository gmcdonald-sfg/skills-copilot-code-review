---
applyTo: "backend/**/*,*.py"
---

## Backend Guidelines

- All API endpoints must be defined in the `routers` folder.
- Load example database content from the `database.py` file.
- Log detailed error information on the server, and return appropriate HTTP status codes and sanitized error messages to the frontend. Never expose stack traces, internal implementation details, or sensitive data in API responses.
- Ensure all APIs are explained in the documentation.
- Verify changes in the backend are reflected in the frontend (`src/static/**`). If possible breaking changes are found, mention them to the developer.