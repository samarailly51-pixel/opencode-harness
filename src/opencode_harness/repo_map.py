from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import fnmatch
import re


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "runs",
    "venv",
}

DEFAULT_IGNORE_FILES = {
    "*.lock",
    "*.min.js",
    "*.pyc",
    "*.pyo",
}

LANGUAGE_BY_SUFFIX = {
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".css": "css",
    ".go": "go",
    ".html": "html",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".json": "json",
    ".md": "markdown",
    ".py": "python",
    ".rs": "rust",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".yaml": "yaml",
    ".yml": "yaml",
}


@dataclass(frozen=True)
class RepoFile:
    path: str
    language: str
    lines: int
    bytes: int
    symbols: list[str]


@dataclass(frozen=True)
class RepoMap:
    root: str
    files: list[RepoFile]

    def render(self, max_files: int = 80, max_symbols_per_file: int = 12) -> str:
        lines = [f"Repository map: {self.root}", f"Files: {len(self.files)}"]
        for file in self.files[:max_files]:
            summary = f"- {file.path} ({file.language}, {file.lines} lines)"
            if file.symbols:
                symbols = ", ".join(file.symbols[:max_symbols_per_file])
                summary += f": {symbols}"
            lines.append(summary)
        if len(self.files) > max_files:
            lines.append(f"... {len(self.files) - max_files} more files")
        return "\n".join(lines)


def build_repo_map(workspace: Path, max_file_bytes: int = 250_000) -> RepoMap:
    root = workspace.resolve()
    files: list[RepoFile] = []
    for file_path in sorted(root.rglob("*"), key=lambda item: str(item).lower()):
        if not file_path.is_file() or _is_ignored(root, file_path):
            continue
        relative = file_path.relative_to(root).as_posix()
        if _matches_any(relative, DEFAULT_IGNORE_FILES):
            continue
        size = file_path.stat().st_size
        language = LANGUAGE_BY_SUFFIX.get(file_path.suffix.lower(), "text")
        symbols: list[str] = []
        line_count = 0
        if size <= max_file_bytes:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            line_count = len(text.splitlines())
            symbols = extract_symbols(text, language)
        files.append(
            RepoFile(
                path=relative,
                language=language,
                lines=line_count,
                bytes=size,
                symbols=symbols,
            )
        )
    return RepoMap(root=str(root), files=files)


def pack_context(repo_map: RepoMap, query: str, max_chars: int = 6000) -> str:
    terms = _query_terms(query)
    scored = sorted(
        repo_map.files,
        key=lambda file: (_score_file(file, terms), -file.lines, file.path),
        reverse=True,
    )
    header = repo_map.render(max_files=20)
    selected: list[str] = [header, "", "Likely relevant files:"]
    for file in scored:
        if _score_file(file, terms) <= 0 and len(selected) > 4:
            break
        entry = f"- {file.path}"
        if file.symbols:
            entry += ": " + ", ".join(file.symbols[:8])
        selected.append(entry)
        if len("\n".join(selected)) >= max_chars:
            break
    return "\n".join(selected)[:max_chars]


def extract_symbols(text: str, language: str) -> list[str]:
    if language == "python":
        patterns = [
            r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)",
        ]
    elif language in {"javascript", "typescript"}:
        patterns = [
            r"^\s*export\s+class\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"^\s*class\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"^\s*export\s+function\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"^\s*function\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"^\s*(?:export\s+)?const\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=",
        ]
    elif language == "markdown":
        patterns = [r"^(#{1,3})\s+(.+)"]
    else:
        patterns = []

    symbols: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            value = match.group(match.lastindex or 1).strip()
            if value and value not in symbols:
                symbols.append(value)
    return symbols[:40]


def _is_ignored(root: Path, file_path: Path) -> bool:
    relative_parts = file_path.relative_to(root).parts
    return any(part in DEFAULT_IGNORE_DIRS for part in relative_parts[:-1])


def _matches_any(path: str, patterns: set[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _query_terms(query: str) -> set[str]:
    return {term.lower() for term in re.findall(r"[A-Za-z0-9_]{3,}", query)}


def _score_file(file: RepoFile, terms: set[str]) -> int:
    haystack = " ".join([file.path, file.language, *file.symbols]).lower()
    score = sum(3 for term in terms if term in haystack)
    if file.path.lower().endswith(("readme.md", "pyproject.toml", "package.json")):
        score += 1
    return score
