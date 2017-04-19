# Contributing to data-migrator

The following is a set of guidelines for contributing to data-migrator.


## Submitting an Issue

1. Provide a small self **sufficient** code + data example to **reproduce** the issue.
2. Use the issue tracker to file the issue at [github](https://github.com/schubergphilis/data-migrator/issues/new)

If the problem cannot be reliably reproduced, the issue will be marked as `question`.

If the problem is not related to request the issue will be marked as `help wanted`.


## Submitting a Pull Request

1. In all of the cases your PR **needs tests** and **documentation**. Please add both if you add code
2. Run `make test` locally. Fix any errors before pushing to GitHub.
3. After submitting the PR a build will be triggered on Circle CI. Wait for it to ends and make sure all jobs are passing.
4. Check if code quality is retained at Codacy.

-----------------------------------------


## Becoming a Contributor

You can become a contributor, just make some valuable contributions and ask for it to become one.


## Rules

There are a few basic ground-rules for contributors:

1. Commit messages reflect intent and all intent is documented in issues, even after the fact
1. **Any** change should be added through Pull Request, from a separate branch from master.
1. **No `--force` pushes** or modifying the Git history in any way.
1. **Non-master branches** ought to be used for ongoing work.
1. All modules, functions, and methods should be well documented reStructuredText for
Sphinx AutoDoc with Google Napoleon conventions.
1. Rebase your PRs and preferably squash them.

## Releases

Declaring formal releases remains the prerogative of the project maintainer.

Everyone interacting with this codebase, issue trackers,
chat rooms, and mailing lists is expected to follow the
[Code of Conduct](http://data-migrator.readthedocs.io/en/latest/code-of-conduct.html).
