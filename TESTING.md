# Testing Workflow

This repository currently does not include an automated test suite.

## Local checks

Run these basic checks from the repository root:

```bash
python -m pip install -r requirements.txt
python -m compileall app
```

If `requirements.txt` is not present, skip the install step and ensure your virtual environment is active before running checks.

## Expected behavior

- `compileall` should complete without syntax errors.
- If errors appear, fix code issues and rerun the command.
