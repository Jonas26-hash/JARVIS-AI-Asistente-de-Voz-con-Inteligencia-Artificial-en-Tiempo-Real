"""codebase.py — Code project indexing and search."""
from __future__ import annotations
import os, json, re
from pathlib import Path

_DB_FILE = Path(__file__).resolve().parent.parent / "config" / "codebase_index.json"


def _load_index() -> dict:
    try:
        return json.loads(_DB_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_index(index: dict) -> None:
    _DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    _DB_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")


def _index_project(path: str) -> dict:
    path = Path(path)
    if not path.is_dir():
        return {"error": "Ruta no válida"}
    files = []
    for ext in ("*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.c", "*.cpp", "*.h", "*.html", "*.css", "*.json", "*.yaml", "*.yml", "*.md", "*.rs", "*.go", "*.rb", "*.php"):
        files.extend(path.rglob(ext))
    entries = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            entries.append({
                "path": str(f.relative_to(path)),
                "size": f.stat().st_size,
                "lines": len(content.splitlines()),
                "snippet": content[:500],
            })
        except Exception:
            pass
    return {"root": str(path), "files": entries, "total": len(entries)}


def codebase(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "list")
    path = parameters.get("path", "")
    name = parameters.get("name", "")
    query = parameters.get("query", "")
    symbol = parameters.get("symbol", "")
    project = parameters.get("project", "")
    file_path = parameters.get("file_path", "")

    index = _load_index()

    if action == "index":
        if not path:
            return "Falta path del proyecto."
        pname = name or Path(path).name
        index[pname] = _index_project(path)
        _save_index(index)
        total = index[pname].get("total", 0)
        return f"Proyecto '{pname}' indexado: {total} archivos."

    elif action == "list":
        if not index:
            return "No hay proyectos indexados."
        return "Proyectos:\n" + "\n".join(f"- {n} ({v.get('total',0)} archivos)" for n, v in index.items())

    elif action == "info":
        if project not in index:
            return f"Proyecto '{project}' no encontrado."
        p = index[project]
        return f"{project}: {p.get('total',0)} archivos en {p.get('root','?')}"

    elif action == "search":
        if not query:
            return "Falta query."
        results = []
        for pname, pdata in index.items():
            for f in pdata.get("files", []):
                if query.lower() in f.get("snippet", "").lower():
                    results.append(f"{pname}: {f['path']}")
        if not results:
            return f"Sin resultados para '{query}'."
        return f"Resultados para '{query}':\n" + "\n".join(results[:20])

    elif action == "find_symbol":
        if not symbol or not project:
            return "Falta symbol y project."
        pdata = index.get(project, {})
        results = []
        for f in pdata.get("files", []):
            for line in f.get("snippet", "").splitlines():
                if symbol in line:
                    results.append(f"{f['path']}: {line.strip()[:100]}")
        return f"'{symbol}' encontrado en:\n" + "\n".join(results[:20]) if results else f"No se encontró '{symbol}'."

    elif action == "remove":
        if name in index:
            del index[name]
            _save_index(index)
            return f"Proyecto '{name}' eliminado."
        return f"Proyecto '{name}' no encontrado."

    return f"Codebase action '{action}' completado."
