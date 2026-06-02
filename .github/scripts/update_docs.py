"""
AI Documentation Updater
Reads the git diff, calls GitHub Models, and writes updated /docs files.
Attributes changelog entries to the GitHub actor who triggered the push.
Preserves any manual doc edits that arrived in the same commit.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

DOCS_DIR = "docs"
DIFF_FILE = "changes.diff"
MANUAL_DOCS_DIFF_FILE = "docs_manual_changes.diff"
MODEL_URL = "https://models.inference.ai.azure.com/chat/completions"
# Switch to "gpt-5-mini" once Copilot Pro is active (12 req/day limit applies).
MODEL_ID = "gpt-4o-mini"
DOC_FILES = ["Home.md", "overview.md", "api-reference.md", "changelog.md"]
MAX_DIFF_CHARS = 5000   # increased — mixed-type diffs (HTML + CSS + XML) can be larger
MAX_DOC_CHARS = 1500


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def read_file_safe(path: str) -> str:
    """Return file content, or empty string if file doesn't exist."""
    try:
        return read_file(path)
    except FileNotFoundError:
        return ""


def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def get_git_info() -> tuple[str, str]:
    """Return (author_display_name, commit_subject) from the latest git commit."""
    try:
        name = subprocess.check_output(
            ["git", "log", "-1", "--format=%an"], text=True
        ).strip()
        subject = subprocess.check_output(
            ["git", "log", "-1", "--format=%s"], text=True
        ).strip()
        return name, subject
    except subprocess.SubprocessError:
        return "unknown", ""


def build_prompt(
    diff: str,
    docs: dict,
    manual_doc_changes: str,
    actor: str,
    author_name: str,
    commit_subject: str,
) -> str:
    docs_block = "\n\n".join(
        f"### {name}\n{content[:MAX_DOC_CHARS]}" for name, content in docs.items()
    )

    attribution = f"@{actor} ({author_name})"
    commit_line = f" Commit message: \"{commit_subject}\"." if commit_subject else ""

    manual_section = ""
    if manual_doc_changes.strip():
        manual_section = (
            f"\n\n---\n"
            f"IMPORTANT: {attribution} also manually edited documentation files in this same push."
            f" Their manual edits are shown below in diff format."
            f" You MUST preserve and incorporate these changes — do NOT revert or ignore them:\n"
            f"```diff\n{manual_doc_changes[:2000]}\n```"
        )

    return (
        f"{attribution} pushed a change to the codebase.{commit_line}"
        f" Update the documentation to reflect the code changes.\n\n"
        f"Code diff:\n```diff\n{diff[:MAX_DIFF_CHARS]}\n```"
        f"{manual_section}\n\n"
        "Current documentation:\n"
        f"{docs_block}\n\n"
        "Rules:\n"
        "- Return a JSON object where keys are filenames and values are full updated markdown.\n"
        "- Only include files that actually need changes — omit unchanged files.\n"
        f"- For changelog.md: add a new entry under [Unreleased] in this exact format:\n"
        f"  '- **{attribution}**: <one-line summary of what changed>'\n"
        "- For api-reference.md: document changes across ALL file types:\n"
        "    Python (.py)          → functions, classes, methods, parameters, return types\n"
        "    JavaScript/TypeScript → exported functions, classes, interfaces, modules\n"
        "    HTML (.html)          → new pages, components, form structures, template purpose\n"
        "    CSS/SCSS (.css/.scss) → new layout classes, design tokens, component styles\n"
        "    XML (.xml)            → new views, models, configuration sections (e.g. Odoo views)\n"
        "    SQL (.sql)            → new tables, columns, procedures, views\n"
        "  Only include what is relevant to a developer using or extending this codebase.\n"
        "- PRESERVE any manually written content — do not remove or revert human edits.\n"
        "- Keep the existing markdown structure and style.\n"
        "- Return ONLY valid JSON. No preamble, no code fences around the JSON."
    )


def call_model(token: str, prompt: str) -> dict:
    payload = json.dumps({
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": "You are a technical documentation writer. Return only valid JSON as instructed.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }).encode()

    req = urllib.request.Request(
        MODEL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"GitHub Models API error {e.code}: {error_body}") from e

    raw = body["choices"][0]["message"]["content"]

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Model returned invalid JSON: {raw[:200]}") from e


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    actor = os.environ.get("GITHUB_ACTOR", "unknown")
    author_name, commit_subject = get_git_info()

    diff = read_file(DIFF_FILE).strip()
    if not diff:
        print("No code diff — nothing to update.")
        return

    manual_doc_changes = read_file_safe(MANUAL_DOCS_DIFF_FILE).strip()
    if manual_doc_changes:
        print(f"Manual doc changes detected ({len(manual_doc_changes)} chars) — will preserve them.")

    print(f"Code diff: {len(diff)} chars | Actor: @{actor} ({author_name})")

    docs = {f: read_file_safe(f"{DOCS_DIR}/{f}") for f in DOC_FILES}
    prompt = build_prompt(diff, docs, manual_doc_changes, actor, author_name, commit_subject)

    print(f"Calling {MODEL_ID}...")
    updates = call_model(token, prompt)

    if not updates:
        print("Model returned no updates.")
        return

    for filename, content in updates.items():
        if filename not in DOC_FILES:
            print(f"Skipping unknown file from model: {filename}")
            continue
        write_file(f"{DOCS_DIR}/{filename}", content)
        print(f"Updated {filename}")


if __name__ == "__main__":
    main()
