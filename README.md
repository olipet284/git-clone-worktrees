# git-clone-worktrees

Clone a Git repository as a bare repository plus a worktree for its remote
default branch. This keeps the repository metadata in `<repo>/.git` and lets
additional branches become sibling worktrees.

## Requirements

- Bash
- Git
- GNU Coreutils (`mv -T`)

## Install

```bash
./setup.sh
```

The installer links `bin/git-clone-worktrees` to
`~/.local/bin/git-clone-worktrees`. Ensure that `~/.local/bin` is on `PATH`. If
that command path already contains another file or symlink, the installer
preserves it under
`${XDG_STATE_HOME:-$HOME/.local/state}/git-clone-worktrees/backups`.

## Use

```bash
git clone-worktrees <url> [parent-directory]
```

The parent defaults to the current directory, which the command leaves
unchanged. HTTPS and SSH Git URLs are supported. The repository name comes from
the URL; its destination must not already exist. The remote must have a
committed default branch. A worktree is created at
`<parent>/<repo>/<branch-with-slashes-replaced-by-hyphens>`, while Git retains
the original branch name and configures its upstream.

Notes in the outer repository directory are outside Git worktrees. From the
default worktree, use `wt switch --create <branch>` for new worktrees. Accept
Worktrunk's first-use prompt to configure this project's worktrees as siblings
of the default worktree. Git's ordinary `git switch` and `git clone` remain
available.

## Check

```bash
python3 tests/check-worktrees.py
```
