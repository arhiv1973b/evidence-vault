from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def handshake() -> bool:
    """Try a handshake with a local harness binary, fallback to checking git availability."""
    harness = Path(__file__).parent / "bin" / "localharness"
    if harness.exists():
        try:
            subprocess.run([str(harness), "--handshake"], check=True)
            print("Handshake with local harness succeeded.")
            return True
        except Exception as e:
            print(f"Handshake with harness failed: {e}", file=sys.stderr)
    git_bin = shutil.which("git")
    if git_bin:
        try:
            subprocess.run([git_bin, "--version"], check=True, stdout=subprocess.DEVNULL)
            print("Git is available — handshake OK.")
            return True
        except Exception as e:
            print(f"Git handshake failed: {e}", file=sys.stderr)
    else:
        print("Neither harness nor git found; handshake failed.", file=sys.stderr)
    return False


def run_build(cmd: str) -> None:
    print(f"Running site build: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}", file=sys.stderr)
        sys.exit(e.returncode)


def install_git_hook(hook_type: str = "pre-push") -> None:
    try:
        repo = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        print("Not inside a git repository.", file=sys.stderr)
        return
    hooks_dir = Path(repo.stdout.strip()) / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / hook_type
    hook_content = """#!/bin/sh
# Antigravity: run site build before push
ag site --handshake || { echo 'Antigravity site build failed'; exit 1; }
"""
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)
    print(f"Installed {hook_type} hook at {hook_path}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="ag", description="Antigravity helper CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_site = sub.add_parser("site", help="Site commands")
    p_site.add_argument("--build-cmd", default=None, help="Shell command to build the site")
    p_site.add_argument("--handshake", action="store_true", help="Run handshake before build")
    p_site.add_argument("--install-hook", action="store_true", help="Install git pre-push hook to run this command")

    s_git = sub.add_parser("git-install-hook", help="Install git hook")
    s_git.add_argument("--hook", default="pre-push")

    args = parser.parse_args(argv)
    if args.cmd == "site":
        if args.handshake:
            ok = handshake()
            if not ok:
                sys.exit(2)
        if args.install_hook:
            install_git_hook()
            return
        build_cmd = args.build_cmd or os.environ.get("ANTIGRAVITY_SITE_BUILD_CMD") or "echo 'No build command configured'"
        run_build(build_cmd)
    elif args.cmd == "git-install-hook":
        install_git_hook(args.hook)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
