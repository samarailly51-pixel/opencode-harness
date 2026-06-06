from __future__ import annotations

from typing import Any

from .mcp import ExternalToolSpec


def _string(description: str) -> dict[str, str]:
    return {"type": "string", "description": description}


def _object(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


TOOL_DESCRIPTIONS: dict[str, str] = {
    "list_files": "List files and directories at a relative workspace path.",
    "read_file": "Read a UTF-8 text file inside the workspace.",
    "search_text": "Search for literal text inside workspace files.",
    "write_file": "Write a UTF-8 text file. Requires write permission.",
    "replace_text": "Replace the first occurrence of text in a file. Requires write permission.",
    "apply_patch": "Apply a unified diff patch. Requires write permission.",
    "todo_set": "Replace the session todo list.",
    "todo_list": "Read the session todo list.",
    "repo_map": "Return a compact repository map.",
    "context_pack": "Return repository context relevant to a query.",
    "shell": "Run a policy-gated shell command.",
    "git_diff": "Return git diff for the workspace.",
    "finish": "Finish the task with a short summary.",
}


TOOL_PARAMETERS: dict[str, dict[str, Any]] = {
    "list_files": _object({"path": _string("Relative path to list.")}, required=[]),
    "read_file": _object({"path": _string("Relative file path.")}, required=["path"]),
    "search_text": _object(
        {
            "pattern": _string("Literal text pattern."),
            "path": _string("Relative directory path."),
        },
        required=["pattern"],
    ),
    "write_file": _object(
        {
            "path": _string("Relative file path."),
            "content": _string("New file content."),
        },
        required=["path", "content"],
    ),
    "replace_text": _object(
        {
            "path": _string("Relative file path."),
            "old": _string("Text to replace."),
            "new": _string("Replacement text."),
        },
        required=["path", "old", "new"],
    ),
    "apply_patch": _object({"patch": _string("Unified diff patch.")}, required=["patch"]),
    "todo_set": _object(
        {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": _string("Todo title."),
                        "status": _string("pending, in_progress, done, or blocked."),
                    },
                    "required": ["title"],
                },
            }
        },
        required=["items"],
    ),
    "todo_list": _object({}, required=[]),
    "repo_map": _object({}, required=[]),
    "context_pack": _object({"query": _string("Task or topic to pack context for.")}, required=[]),
    "shell": _object({"command": _string("Shell command to run.")}, required=["command"]),
    "git_diff": _object({}, required=[]),
    "finish": _object({"summary": _string("Final task summary.")}, required=["summary"]),
}


def openai_tool_schemas(extra_tools: list[ExternalToolSpec] | None = None) -> list[dict[str, Any]]:
    schemas = [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": TOOL_DESCRIPTIONS[name],
                "parameters": TOOL_PARAMETERS[name],
            },
        }
        for name in TOOL_DESCRIPTIONS
    ]
    for tool in extra_tools or []:
        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
        )
    return schemas


def anthropic_tool_schemas(extra_tools: list[ExternalToolSpec] | None = None) -> list[dict[str, Any]]:
    schemas = [
        {
            "name": name,
            "description": TOOL_DESCRIPTIONS[name],
            "input_schema": TOOL_PARAMETERS[name],
        }
        for name in TOOL_DESCRIPTIONS
    ]
    for tool in extra_tools or []:
        schemas.append(
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
        )
    return schemas
