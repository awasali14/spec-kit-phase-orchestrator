# Git Branch Plan

Use two long-lived branches for this project.

## Branches

1. `main`

   Production branch for released or release-ready extension code.

2. `dev`

   Development branch for improvements, bug fixes, local testing, and draft work before it is moved to `main`.

## Normal Workflow

1. Start new work from `dev`.

   ```bash
   git switch dev
   git pull origin dev
   ```

2. Make the change locally.

3. Review the changed files.

   ```bash
   git status
   git diff
   ```

4. Run the relevant tests or manual checks.

5. Commit on `dev`.

   ```bash
   git add <files>
   git commit
   ```

6. Push `dev`.

   ```bash
   git push origin dev
   ```

7. When the work is tested, merge `dev` into `main`.

   ```bash
   git switch main
   git pull origin main
   git merge dev
   git push origin main
   ```

## Commit Message Format

Use a short subject and a clear body.

```text
type: short summary

Explain what changed and why. Mention important test results or manual checks.
```

Common types:

1. `chore`: setup, metadata, tooling, or maintenance.
2. `feat`: new user-facing functionality.
3. `fix`: bug fix.
4. `docs`: documentation-only change.
5. `test`: test-only change.

Example:

```text
chore: scaffold extension repository

Create the initial public repository structure for the phase orchestrator
extension and document the branch workflow for future development.
```
