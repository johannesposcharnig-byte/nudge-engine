# GitHub Automation Workflow

## Recommendation

Use controlled automatic pushes, not blind pushes on every file save.

Reason:

- every push should be reproducible
- tests must pass first
- generated documentation should explain what changed
- customer data, PII, vault files and local artefacts must never be pushed

## What Is Implemented

### 1. Git Ignore Boundary

`.gitignore` excludes:

- Python caches
- macOS files
- local environments
- logs and databases
- PII/vault/customer raw data folders
- local dashboard report exports

### 2. Safe Checkpoint Push

Use:

```bash
bash scripts/safe_checkpoint_push.sh "your commit message"
```

The script does this:

1. verifies that the folder is a git repository
2. verifies that `origin` exists
3. runs all tests
4. runs Python compile check
5. updates `CHANGELOG_AUTO.md`
6. commits all staged changes
7. pushes to the current branch on `origin`

If tests fail, the script stops before commit and push.

### 3. Automated Change Documentation

`scripts/generate_change_summary.py` appends a compact entry to:

```text
CHANGELOG_AUTO.md
```

The entry includes:

- timestamp
- test status
- latest commit
- changed files
- diff stat

### 4. GitHub Validation

`.github/workflows/validate.yml` runs on push and pull request:

- full unit test discovery
- Python compile check

## Recommended Usage

### Normal Development

Use the safe checkpoint script after a meaningful working step:

```bash
bash scripts/safe_checkpoint_push.sh "checkpoint: analysis service and report pipeline"
```

### Larger Changes

Use a branch:

```bash
git checkout -b feature/dashboard-api
bash scripts/safe_checkpoint_push.sh "feature: connect dashboard to analysis api"
```

Then open a pull request in GitHub.

## What Not To Automate Yet

Do not push automatically on every file save.

That would create noisy history and can push half-finished work or local mistakes.

Better rule:

Push automatically only after:

- tests pass
- compile check passes
- change log is generated
- sensitive files are excluded

## Still Needed Before First Push

1. Initialize git if needed.
2. Create a private GitHub repository.
3. Add it as `origin`.
4. Run the safe checkpoint script.

