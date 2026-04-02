# Contributing to Autonomous Data Analyst Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs/screenshots if applicable

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Explain:
   - Use case
   - Proposed solution
   - Alternative approaches
   - Why this would be valuable

### Code Contributions

1. **Fork the repository**
2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation
   - Add comments for complex logic

4. **Test your changes**
   ```bash
   pytest tests/ -v
   flake8 backend/app
   black backend/app
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new safety check for X"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Use PR template
   - Link related issues
   - Describe changes clearly
   - Ensure CI passes

## Code Style

### Python

- Follow PEP 8
- Use black for formatting
- Maximum line length: 120 characters
- Use type hints where appropriate
- Add docstrings for functions

Example:
```python
def calculate_total(items: List[Item]) -> float:
    """
    Calculate total price of items.
    
    Args:
        items: List of items to sum
    
    Returns:
        Total price as float
    """
    return sum(item.price for item in items)
```

### Commit Messages

Format: `<type>: <description>`

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `style:` - Formatting changes
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for OpenAI GPT-4
fix: correct validation for nested imports
docs: update security guidelines
test: add edge case for AST validator
```

## Testing Guidelines

- Write tests for all new features
- Maintain test coverage above 80%
- Include both positive and negative test cases
- Use descriptive test names

## Documentation

- Update README.md for user-facing changes
- Update DEVELOPMENT.md for developer changes
- Add docstrings to new functions
- Include code examples where helpful

## Security

- Report security issues privately (see SECURITY.md)
- Never commit secrets or API keys
- Add tests for security-critical code
- Follow principle of least privilege

## Review Process

1. Maintainer reviews code
2. CI checks must pass
3. At least one approval required
4. Feedback addressed
5. Merged to main

## Getting Help

- Ask questions in GitHub Discussions
- Join community chat (if available)
- Check existing documentation
- Reach out to maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in documentation

Thank you for contributing! 🙏
