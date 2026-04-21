from __future__ import annotations

import subprocess
from pathlib import Path


def run_git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout.strip()


def ensure_repo(repo_url: str, repo_dir: Path) -> None:
    if (repo_dir / ".git").exists():
        run_git(["fetch", "--all", "--prune"], cwd=repo_dir)
        return
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", repo_url, str(repo_dir)],
        text=True,
        capture_output=True,
        check=True,
    )


def detect_default_remote_branch(repo_dir: Path) -> str:
    try:
        ref = run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=repo_dir)
        return ref.rsplit("/", 1)[-1]
    except subprocess.CalledProcessError:
        branches = run_git(["branch", "-r"], cwd=repo_dir).splitlines()
        clean = [b.strip() for b in branches]
        if "origin/main" in clean:
            return "main"
        if "origin/master" in clean:
            return "master"
        raise


def checkout_default_branch(repo_dir: Path) -> str:
    branch = detect_default_remote_branch(repo_dir)
    run_git(["checkout", branch], cwd=repo_dir)
    run_git(["reset", "--hard", f"origin/{branch}"], cwd=repo_dir)
    return branch


def head_commit(repo_dir: Path) -> str:
    return run_git(["rev-parse", "HEAD"], cwd=repo_dir)


def changed_pep_paths(repo_dir: Path, old_commit: str, new_commit: str) -> list[tuple[str, str]]:
    if old_commit == new_commit:
        return []
    out = run_git(
        ["diff", "--name-status", old_commit, new_commit, "--", "pep-*.rst", "peps/pep-*.rst"],
        cwd=repo_dir,
    )
    changes: list[tuple[str, str]] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            changes.append(("D", parts[1]))
            changes.append(("A", parts[2]))
        elif len(parts) >= 2:
            changes.append((status[0], parts[1]))
    return changes
