# Contributing Guidelines

Thanks for your interest in contributing to Mouser. This document explains the preferred workflow and standards to make contributions fast and smooth.

## Table of Contents
- Purpose
- Getting started
- Development workflow
- Issues & feature requests
- Pull request process
- Tests & quality
- Style & commit messages
- Contact

## Purpose
Contributions to Mouser can include:

- Bug fixes
- New feature implementations
- Documentation or README improvements
- Code refactoring or test coverage enhancements
- Maintenance and cleanup tasks

All contributions, big or small, help strengthen the project’s community and functionality.

## Getting started

1. Fork the repository and clone your fork:
```bash
git clone https://github.com/<your-username>/Mouser.git
cd Mouser
```
2. Create and switch to a new branch:
```bash
git checkout -b feature/feature_name
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the project locally to verify setup:
```bash
python main.py
```
5. Run tests before making changes.

## Development workflow
- Work on small, focused branches per issue or feature.
- Branch naming convention:
   - feature/... for new features
   - fix/... for bug fixes
   - docs/... for documentation updates
   - chore/... for maintenance tasks
- Rebase or merge the latest main branch regularly to stay up-to-date.

## Issues & feature requests

- Check the [Issues tab](https://github.com/oss-slu/Mouser/issues) before creating a new one.
- When submitting a new issue, include:
  - A clear and descriptive title
  - Steps to reproduce (for bugs)
  - Expected vs. actual behavior
  - System details (OS, Python version, etc.)
- Tag issues appropriately (e.g., bug, enhancement, documentation)

## Pull request process
- Base PRs on the main branch of your fork.
- Include a clear description of:
  - What the change does
  - Why it is needed
  - Any migration or compatibility notes
- Link to the related issue(s) with "Closes #<issue>" when appropriate.
- Keep PRs small and focused. One logical change per PR.
- Request reviews from maintainers or relevant reviewers.

## Tests & quality
- Add or update tests for any bug fix or feature.
- Run the full test suite locally and ensure all tests pass before opening a PR.
- Fix linter and formatting issues.

## Style & commit messages
- Follow existing project coding conventions.
- Commit message format (brief):
  - type(scope): short summary
  - Eg: fix(parser): handle empty input
- Use present-tense, imperative mood.

## Reviewing & merging
- Maintainers will review and request changes as needed.
- Address review comments promptly and update the PR.
- Squash or keep commits tidy per maintainer preference.

## Licensing & ownership
- Contributions are submitted under the project's license. Do not add third-party code without proper licensing.

## Contact
- For questions, open an issue with the "help wanted" label.