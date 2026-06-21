"""code_helper.py — Write, edit, explain, run, and build code."""
from __future__ import annotations
import os, subprocess, sys, json
from pathlib import Path


def code_helper(parameters=None, player=None, speak=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "auto")
    description = parameters.get("description", "")
    language = parameters.get("language", "python")
    output_path = parameters.get("output_path", "")
    file_path = parameters.get("file_path", "")
    code = parameters.get("code", "")
    args = parameters.get("args", "")
    timeout = parameters.get("timeout", 30)

    try:
        if action == "write":
            if not description or not output_path:
                return "Falta description o output_path."
            return f"Usá file_controller action=create_file para escribir en {output_path} con el contenido generado."

        elif action == "edit":
            if not file_path or not os.path.isfile(file_path):
                return f"Archivo no encontrado: {file_path}"
            old = parameters.get("description", "")
            new = parameters.get("code", "")
            if old and new:
                content = Path(file_path).read_text(encoding="utf-8")
                content = content.replace(old, new)
                Path(file_path).write_text(content, encoding="utf-8")
                return f"Archivo editado: {file_path}"
            return "Falta description (texto a reemplazar) y code (nuevo texto)."

        elif action == "explain":
            target = file_path or code
            if not target:
                return "Falta file_path o code."
            if file_path and os.path.isfile(file_path):
                code = Path(file_path).read_text(encoding="utf-8")
            lines = code.split("\n")
            return f"Explicación de {len(lines)} líneas:\n```\n{code[:2000]}\n```"

        elif action == "run":
            target = file_path or output_path
            if not target or not os.path.isfile(target):
                return f"Archivo no encontrado: {target}"
            cmd = [sys.executable, target] + (args.split() if args else [])
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            out = r.stdout.strip() or r.stderr.strip()
            return f"Salida ({len(out)} chars):\n{out[:1000]}"

        elif action == "build":
            target = output_path or file_path
            if not target:
                return "Falta output_path o file_path."
            lang_cmds = {"python": ["python", "-m", "py_compile", target], "node": ["node", "--check", target]}
            cmd = lang_cmds.get(language, [language, target])
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if r.returncode == 0:
                return f"Build exitoso: {target}"
            return f"Error de build: {r.stderr[:500]}"

        return f"Code Helper action '{action}' completado."
    except subprocess.TimeoutExpired:
        return "Tiempo de ejecución agotado."
    except Exception as e:
        return f"Error: {e}"
