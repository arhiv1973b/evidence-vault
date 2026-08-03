from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def handshake() -> bool:
    """Try a handshake with a local harness binary, fallback to checking git availability.

    This function avoids any calls to model APIs to prevent unexpected quota usage.
    """
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


def _lazy_import_model_router():
    # Import the model router only when explicitly requested to avoid quotas
    try:
        from google.antigravity import model_router

        return model_router
    except Exception as e:
        print(f"Model router import failed: {e}", file=sys.stderr)
        return None


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
    p_site.add_argument("--use-models", action="store_true", help="(Opt-in) Run a small model test via configured model router before building")

    s_git = sub.add_parser("git-install-hook", help="Install git hook")
    s_git.add_argument("--hook", default="pre-push")

    s_model = sub.add_parser("model-test", help="Run a small opt-in model test using the configured router")
    s_model.add_argument("--prompt", default="Ping from Antigravity CLI", help="Prompt to send to the model (opt-in)")

    args = parser.parse_args(argv)
    if args.cmd == "site":
        if args.handshake:
            ok = handshake()
            if not ok:
                sys.exit(2)
        if args.install_hook:
            install_git_hook()
            return
        if args.use_models:
            # Explicit opt-in: import and run a tiny test to validate models and routing
            mr = _lazy_import_model_router()
            if mr:
                router = mr.get_default_router()

                def _call(model_name, prompt):
                    # Minimal model invocation to validate routing. Keeps payload tiny.
                    try:
                        import importlib
                        genai = importlib.import_module("google.genai")
                        client = genai.create_client()
                        resp = client.generate("text-bison@001", prompt=prompt)  # placeholder API
                        return resp
                    except Exception as e:
                        raise

                try:
                    result = router.run_with_fallback(_call, args.build_cmd or "test")
                    print("Model test succeeded (opt-in).")
                except Exception as e:
                    print(f"Model test failed: {e}", file=sys.stderr)
        build_cmd = args.build_cmd or os.environ.get("ANTIGRAVITY_SITE_BUILD_CMD") or "echo 'No build command configured'"
        run_build(build_cmd)
    elif args.cmd == "git-install-hook":
        install_git_hook(args.hook)
    elif args.cmd == "model-test":
        mr = _lazy_import_model_router()
        if not mr:
            print("Model router not available.")
            sys.exit(2)
        router = mr.get_default_router()

        def _call(model_name, prompt):
            import importlib
            genai = importlib.import_module("google.genai")
            client = genai.create_client()
            # NOTE: This is opt-in testing only; keep payload small to limit quota usage.
            return client.generate("text-bison@001", prompt=prompt)

        try:
            resp = router.run_with_fallback(_call, args.prompt)
            print("Model response received (opt-in).")
        except Exception as e:
            print(f"Model test failed: {e}", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
