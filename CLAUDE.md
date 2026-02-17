# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository

- **Name**: 2DSD15AFSEE
- **Owner**: iparsons
- **Default Branch**: `master`
- **Remote**: `origin` (Gitea instance via local proxy)

## Project Overview

This is a newly initialized repository with no source code yet committed.

- **Language(s)**: _TBD_
- **Framework(s)**: _TBD_
- **Purpose**: _TBD_

> Update this section as the project takes shape.

## Directory Structure

```
2DSD15AFSEE/
└── CLAUDE.md       # AI assistant guidance (this file)
```

No source code has been committed yet. Update this section as the project structure is established.

## Build & Run

_Add build and run instructions here once the project has a build system._

## Testing

_Add testing instructions here (e.g., `npm test`, `pytest`, `cargo test`)._

## Linting & Formatting

_Add linting/formatting commands here (e.g., `npm run lint`, `ruff check .`)._

## Code Conventions

_Document coding standards, naming conventions, and patterns used in this project._

## Development Workflow

1. **Branch**: Create a feature branch from `master`. AI-driven work uses branches with the pattern `claude/<slug>-<session-id>`.
2. **Develop**: Make changes on the feature branch. Read relevant files before modifying anything.
3. **Test**: Run tests after every modification and ensure they pass before committing.
4. **Commit**: Write clear, descriptive commit messages summarizing the *why*, not just the *what*.
5. **Push**: Push to the remote branch with `git push -u origin <branch-name>`.
6. **PR**: Open a pull request against `master` for review.

### Git Conventions

- Branch names for AI sessions follow: `claude/<descriptor>-<session-id>`
- Always push to the correct branch — pushing to the wrong branch will result in a 403 error.
- Sign commits using the configured SSH signing key.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | AI assistant guidance (this file) |

_Add key files and their purposes as the project grows._

## Notes for AI Assistants

- **Read before editing**: Always read the relevant source files before proposing or making changes.
- **Run tests**: After modifications, run the project's test suite and confirm it passes.
- **Match conventions**: Follow existing code style, naming, and patterns — do not introduce new patterns without good reason.
- **Stay focused**: Keep changes minimal and targeted. Avoid refactoring code unrelated to the current task.
- **No over-engineering**: Do not add features, abstractions, or error handling for hypothetical future scenarios.
- **Update this file**: When the project structure, build system, or workflow changes significantly, update the relevant sections here.
- **Branch discipline**: Develop on the designated feature branch and never push to `master` directly.
- **Commit often**: Make small, logical commits rather than one large commit at the end.
