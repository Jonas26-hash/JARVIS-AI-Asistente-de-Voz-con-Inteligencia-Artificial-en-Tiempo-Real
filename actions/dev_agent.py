"""dev_agent.py — Build complete multi-file projects."""
from __future__ import annotations
import os, subprocess, sys, json
from pathlib import Path


def dev_agent(parameters=None, player=None, speak=None, **kwargs):
    if parameters is None:
        parameters = {}
    description = parameters.get("description", "")
    language = parameters.get("language", "python")
    project_name = parameters.get("project_name", "jarvis_project")
    timeout = parameters.get("timeout", 30)

    if not description:
        return "Falta la descripción del proyecto."

    base = Path.home() / "Documents" / "JARVIS_Projects" / project_name
    base.mkdir(parents=True, exist_ok=True)

    if language == "python":
        main_file = base / "main.py"
        main_file.write_text(f'"""Auto-generated project: {project_name}"""\n\n# {description}\n\n\ndef main():\n    print("Hello from {project_name}!")\n\n\nif __name__ == "__main__":\n    main()\n', encoding="utf-8")
        req_file = base / "requirements.txt"
        if not req_file.exists():
            req_file.write_text("# Dependencies\n")
        readme = base / "README.md"
        readme.write_text(f"# {project_name}\n\n{description}\n")

        if player:
            player.write_log(f"📁 Proyecto creado en: {base}")

        try:
            subprocess.Popen(["code", str(base)], shell=True)
        except Exception:
            pass

        return f"Proyecto '{project_name}' creado en {base}. Abriendo VSCode."

    elif language in ("node", "javascript", "typescript"):
        (base / "index.js").write_text(f"// {description}\nconsole.log('Hello from {project_name}!');\n")
        return f"Proyecto Node.js '{project_name}' creado en {base}."

    elif language in ("html", "web"):
        (base / "index.html").write_text(f"<!DOCTYPE html><html><head><title>{project_name}</title></head><body><h1>{project_name}</h1><p>{description}</p></body></html>")
        (base / "style.css").write_text("/* Styles */\n")
        (base / "script.js").write_text("// Script\n")
        return f"Proyecto web '{project_name}' creado en {base}."

    return f"Lenguaje '{language}' no soportado aún. Proyecto creado en {base}."
