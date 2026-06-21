"""git_control.py — Full Git integration via CLI."""
from __future__ import annotations
import subprocess, os
from pathlib import Path


def _git(repo_path: str, *args) -> str:
    try:
        r = subprocess.run(["git"] + list(args), cwd=repo_path, capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or r.stderr.strip()
    except FileNotFoundError:
        return "Git no está instalado o no está en PATH."
    except subprocess.TimeoutExpired:
        return "Comando git agotó el tiempo de espera."
    except Exception as e:
        return f"Error: {e}"


def git_control(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "status")
    repo_path = parameters.get("repo_path", os.getcwd())
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        return f"No es un repositorio Git: {repo_path}"

    if action == "status":
        return _git(repo_path, "status")

    elif action == "log":
        n = parameters.get("n", 10)
        return _git(repo_path, "log", f"--oneline", f"-{n}")

    elif action == "diff":
        file = parameters.get("file", "")
        staged = parameters.get("staged", False)
        cmd = ["diff"]
        if staged:
            cmd.append("--cached")
        if file:
            cmd.append("--")
            cmd.append(file)
        return _git(repo_path, *cmd)

    elif action == "commit":
        msg = parameters.get("message", "Auto commit")
        add_all = parameters.get("add_all", True)
        if add_all:
            _git(repo_path, "add", "-A")
        return _git(repo_path, "commit", "-m", msg)

    elif action == "add":
        files = parameters.get("files", [])
        if files:
            return _git(repo_path, "add", *files)
        return _git(repo_path, "add", "-A")

    elif action == "branches":
        return _git(repo_path, "branch", "-a")

    elif action == "branch_create":
        name = parameters.get("branch_name", "")
        if name:
            return _git(repo_path, "checkout", "-b", name)
        return "Falta branch_name."

    elif action == "checkout":
        name = parameters.get("branch_name", "")
        if name:
            return _git(repo_path, "checkout", name)
        return "Falta branch_name."

    elif action == "pull":
        remote = parameters.get("remote", "origin")
        return _git(repo_path, "pull", remote)

    elif action == "push":
        remote = parameters.get("remote", "origin")
        return _git(repo_path, "push", remote)

    elif action == "stash":
        sub = parameters.get("sub", "list")
        return _git(repo_path, "stash", sub)

    elif action == "analyze":
        log = _git(repo_path, "log", "--oneline", "-20")
        branches = _git(repo_path, "branch", "-a")
        status = _git(repo_path, "status")
        return f"Rama actual: {_git(repo_path, 'branch', '--show-current')}\n\nCambios:\n{status}\n\nÚltimos commits:\n{log}\n\nBranches:\n{branches}"

    return f"Git action '{action}' completado."
