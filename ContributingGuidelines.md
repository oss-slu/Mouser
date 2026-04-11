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

All contributions, big or small, help strengthen the project's community and functionality.

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
- Use the GitHub issue templates (Bug report / Feature request) to provide the details maintainers need to triage quickly.
- When submitting a new issue, include:
  - A clear and descriptive title
  - Steps to reproduce (for bugs)
  - Expected vs. actual behavior
  - System details (OS, Python version, etc.)
- Tag issues appropriately (e.g., `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`) when you have permission to apply labels.

### Finding something to work on

- Start with issues labeled `good first issue` for small, well-scoped tasks.
- Use `help wanted` to find tasks that maintainers think are ready for external contributors.
- If you want to work on an issue, leave a short comment like: "I'd like to work on this — can you assign me?"

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
- For questions, open a GitHub issue with your question and any relevant context (OS, Python version, screenshots). Maintainers may label it appropriately (for example `question` or `help wanted`).
