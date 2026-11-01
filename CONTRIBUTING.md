# Contributing

Thanks for helping improve the railway track defect detection prototype.

## Before opening an issue or pull request

- Search existing issues and pull requests for a matching report.
- Use the issue templates for bugs and feature requests.
- Do not attach API keys, passwords, private camera footage, or unlicensed datasets.
- Keep changes focused and explain which part of the project they affect: Colab training, Pi inference, dashboard, model artifacts, or hardware.

## Development guidelines

- Python code should follow PEP 8, use descriptive names, and keep hardware-specific behavior behind clear arguments or functions.
- Keep model and dataset paths configurable. Do not embed usernames, home directories, secrets, or device addresses in code.
- Keep the dashboard bound to localhost by default. Document any change that exposes it to a network.
- Keep dataset attribution and the validation/test distinction intact in reports.
- Do not commit generated captures, local training runs, private data, or credentials.

## Pull requests

Use a short, descriptive branch name such as `fix/pi-camera-restart` or `docs/colab-setup`. Include a clear summary, the reason for the change, and the checks you performed. For Pi changes, note the Pi OS and hardware used. For model changes, record the dataset version, split, training settings, and whether values come from validation or test data.

This repository currently has no automated test suite. Do not describe a manual check as an automated test. If a change cannot be checked on the target hardware, state that clearly in the pull request.
