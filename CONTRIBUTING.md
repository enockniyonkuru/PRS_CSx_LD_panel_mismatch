# Contributing Guidelines

Thank you for your interest in this project!

**Project Contact**: enock.niyonkuru@ucsf.edu

## How to Report Issues

Please open an issue on the repository with:
- A clear, descriptive title
- Detailed description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (Python version, OS, installed packages)

Alternatively, email enock.niyonkuru@ucsf.edu with details.

## How to Contribute Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black src/`
6. Lint: `flake8 src/`
7. Commit with clear messages: `git commit -m "Add feature X"`
8. Push and open a pull request

## Code Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Aim for docstrings on public functions
- Keep lines ≤ 100 characters (enforced by Black)

## Testing

All contributions should include tests. Run with:
```bash
pytest -v
```

## Questions?

Open an issue or contact the author.
