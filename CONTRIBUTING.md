# Contributing to EMA Heikin Ashi Strategy

First off, thank you for considering contributing to the EMA Heikin Ashi Strategy project! It's people like you that make this project better.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report:**

* Check the documentation for a list of common questions and problems.
* Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/yourusername/ema-ha-strategy/issues).
* If you're unable to find an open issue addressing the problem, open a new one.

**How Do I Submit A (Good) Bug Report?**

Bugs are tracked as [GitHub issues](https://github.com/yourusername/ema-ha-strategy/issues). Create an issue and provide the following information:

* Use a clear and descriptive title for the issue to identify the problem.
* Describe the exact steps which reproduce the problem in as many details as possible.
* Provide specific examples to demonstrate the steps.
* Describe the behavior you observed after following the steps and point out what exactly is the problem with that behavior.
* Explain which behavior you expected to see instead and why.
* Include screenshots and animated GIFs if possible.
* If the problem is related to performance or memory, include a CPU profile capture with your report.
* If the problem is related to backtesting results, include the configuration file and data sample if possible.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion:**

* Check if the enhancement has already been suggested.
* Determine which repository the enhancement should be suggested in.
* Perform a cursory search to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

**How Do I Submit A (Good) Enhancement Suggestion?**

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title for the issue to identify the suggestion.
* Provide a step-by-step description of the suggested enhancement in as many details as possible.
* Provide specific examples to demonstrate the steps or point out the part of the project that the suggestion is related to.
* Describe the current behavior and explain which behavior you expected to see instead and why.
* Explain why this enhancement would be useful to most users.
* List some other applications where this enhancement exists, if applicable.
* Specify which version of the project you're using.

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible.
* Follow the Python style guide.
* Include unit tests for new features or bug fixes.
* Ensure all tests pass before submitting your PR.
* Maintain or improve code coverage (aim for >95% coverage).
* Run cross-validation for any changes to the backtesting engine.
* End all files with a newline.
* Avoid platform-dependent code.

### Testing Guidelines

* Write unit tests for all new code.
* Use pytest fixtures for common test setup.
* Mock external dependencies in unit tests.
* Write integration tests for complex interactions.
* Run the full test suite before submitting a PR:
  ```bash
  pytest
  ```
* Check code coverage to ensure your changes are well-tested:
  ```bash
  pytest --cov=. --cov-report=term-missing
  ```
* For changes to the backtesting engine, run cross-validation to ensure deterministic results:
  ```bash
  python main.py --validate
  ```

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 🚱 `:non-potable_water:` when plugging memory leaks
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * 💚 `:green_heart:` when fixing the CI build
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security
    * ⬆️ `:arrow_up:` when upgrading dependencies
    * ⬇️ `:arrow_down:` when downgrading dependencies

### Python Styleguide

All Python code should adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).

* Use 4 spaces for indentation (not tabs)
* Use docstrings for all public classes, methods, and functions
* Use type hints for function arguments and return values
* Keep line length to 88 characters or less
* Use single quotes for string literals, except when a string contains single quotes
* Use meaningful variable names
* Add comments for complex code sections

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation.
* Reference functions, classes, and modules in backticks.
* Use section headers to organize content.
* Update documentation when you change code.

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs.
* `enhancement` - Issues that are feature requests.
* `documentation` - Issues or pull requests that are related to documentation.
* `good first issue` - Good for newcomers.
* `help wanted` - Extra attention is needed.
* `invalid` - Issues that are invalid or non-reproducible.
* `question` - Issues that are questions.
* `wontfix` - Issues that will not be worked on.

## Thank You!

Your contributions to open source, large or small, make projects like this possible. Thank you for taking the time to contribute.
