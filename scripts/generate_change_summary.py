"""Generate a compact repository change summary for safe GitHub pushes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG_AUTO.md"


def git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return completed.stderr.strip() or completed.stdout.strip()
    return completed.stdout.strip()


def in_git_repo() -> bool:
    return git(["rev-parse", "--is-inside-work-tree"]) == "true"


def changed_files() -> list[str]:
    status = git(["status", "--short"])
    if not status:
        return []
    return [line.strip() for line in status.splitlines() if line.strip()]


def diff_stat() -> str:
    stat = git(["diff", "--stat", "HEAD"])
    if "fatal:" in stat.lower():
        stat = git(["diff", "--stat", "--cached"])
    return stat or "No diff stat available."


def latest_commit() -> str:
    commit = git(["log", "-1", "--oneline"])
    if "fatal:" in commit.lower():
        return "No commit yet."
    return commit or "No commit yet."


def append_summary(test_status: str, note: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    files = changed_files()
    lines = [
        "",
        f"## {timestamp}",
        "",
        f"- Test status: `{test_status}`",
        f"- Latest commit: `{latest_commit()}`",
    ]
    if note:
        lines.append(f"- Note: {note}")
    lines.extend(["", "### Changed Files", ""])
    if files:
        lines.extend(f"- `{file}`" for file in files)
    else:
        lines.append("- No working-tree changes detected.")
    lines.extend(["", "### Diff Stat", "", "```text", diff_stat(), "```", ""])
    CHANGELOG.write_text(CHANGELOG.read_text() + "\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-status", default="not_run")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    if not in_git_repo():
        append_summary(
            args.test_status,
            args.note or "Generated before git repository initialization.",
        )
        print(f"Updated {CHANGELOG}")
        return 0

    append_summary(args.test_status, args.note)
    print(f"Updated {CHANGELOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
