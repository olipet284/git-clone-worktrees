#!/usr/bin/env python3
"""Exercise clone-worktrees with local remotes and isolated Git configuration."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory(prefix='dotfiles-worktrees.') as tmp:
    base = Path(tmp)
    home = base / 'home'
    home.mkdir()
    env = os.environ | {'HOME': str(home), 'XDG_STATE_HOME': str(home / 'state'), 'GIT_CONFIG_NOSYSTEM': '1', 'PATH': f'{ROOT}/bin:' + os.environ['PATH']}
    def run(*args, ok=True, cwd=base):
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
        assert (result.returncode == 0) == ok, (args, result.stdout, result.stderr)
        return result
    install_bin = home / '.local/bin'
    install_bin.mkdir(parents=True)
    old_command = install_bin / 'git-clone-worktrees'
    old_command.write_text('previous command\n')
    run('bash', str(ROOT / 'setup.sh'))
    assert old_command.is_symlink()
    install_backups = list((home / 'state/git-clone-worktrees/backups').iterdir())
    assert len(install_backups) == 1
    assert (install_backups[0] / 'git-clone-worktrees').read_text() == 'previous command\n'
    run('bash', str(ROOT / 'setup.sh'))
    assert list((home / 'state/git-clone-worktrees/backups').iterdir()) == install_backups
    source = base / 'source'
    run('git', 'init', '-b', 'release/stable', str(source))
    run('git', '-C', str(source), 'config', 'user.name', 'Test')
    run('git', '-C', str(source), 'config', 'user.email', 'test@example.invalid')
    (source / 'file.txt').write_text('hello\n')
    run('git', '-C', str(source), 'add', 'file.txt')
    run('git', '-C', str(source), 'commit', '-m', 'Initial')
    remote = base / 'remote.git'
    run('git', 'clone', '--bare', str(source), str(remote))
    dest = base / 'repos with spaces'
    dest.mkdir()
    run('git', 'clone-worktrees', str(remote), str(dest))
    repo = dest / 'remote'
    worktree = repo / 'release-stable'
    assert (worktree / 'file.txt').read_text() == 'hello\n'
    assert run('git', '-C', str(worktree), 'branch', '--show-current').stdout.strip() == 'release/stable'
    assert run('git', '-C', str(worktree), 'rev-parse', '--abbrev-ref', '@{upstream}').stdout.strip() == 'origin/release/stable'
    assert run('git', '-C', str(worktree), 'status', '--porcelain').stdout == ''
    (repo / 'notes').write_text('keep')
    run('git', 'clone-worktrees', str(remote), str(dest), ok=False)
    assert (repo / 'notes').read_text() == 'keep'
    empty = base / 'empty.git'
    run('git', 'init', '--bare', str(empty))
    result = run('git', 'clone-worktrees', str(empty), str(dest), ok=False)
    assert 'no commits' in result.stderr
    assert not (dest / 'empty').exists()
    assert not list(dest.glob('.git-clone-worktrees.*'))
print('PASS: bare clone, default worktree, tracking, destination protection and empty remote')
