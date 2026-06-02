"""
AI Documentation Updater
Reads the git diff, calls GitHub Models, and writes updated /docs files.
"""

import json
import os
import sys
import urllib.error
import urllib.request

DOCS_DIR = "docs"
DIFF_FILE = "changes.diff"
MODEL_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_ID = "gpt-4o-mini"
DOC_FILES = ["overview.md", "api-reference.md", "changelog.md"]
MAX_DIFF_CHARS = 3000   # keep total prompt well under 4000-token limit
MAX_DOC_CHARS = 1500    # per doc file — prevents oversized prompts as docs grow


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def build_prompt(diff: str, docs: dict) -> str:
    docs_block = "\n\n".join(
        f"### {name}\n{content[:MAX_DOC_CHARS]}" for name, content in docs.items()
    )
    return (
        "A developer pushed code changes to a Python project.\n"
        "Update the documentation so it accurately reflects the new code.\n\n"
        f"Git diff (capped at {MAX_DIFF_CHARS} chars):\n"
        f"```diff\n{diff[:MAX_DIFF_CHARS]}\n```\n\n"
        "Current documentation:\n"
        f"{docs_block}\n\n"
        "Rules:\n"
        "- Return a JSON object where keys are filenames and values are full updated markdown.\n"
        "- Only include files that actually need changes — omit unchanged files.\n"
        "- For changelog.md: add a new dated entry at the top of [Unreleased] summarising what changed.\n"
        "- For api-reference.md: reflect any added, removed, or renamed functions/classes/methods.\n"
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

    diff = read_file(DIFF_FILE).strip()
    if not diff:
        print("No diff in changes.diff — nothing to update.")
        return

    print(f"Diff size: {len(diff)} chars")

    docs = {f: read_file(f"{DOCS_DIR}/{f}") for f in DOC_FILES}
    prompt = build_prompt(diff, docs)

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
