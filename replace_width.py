from pathlib import Path

count = 0

for f in Path(".").rglob("*.py"):
    text = f.read_text(encoding="utf-8", errors="ignore")
    new = text.replace(
        "width="stretch"",
        'width="stretch"',
    ).replace(
        "width="content"",
        'width="content"',
    )

    if new != text:
        f.write_text(new, encoding="utf-8")
        count += 1

print(f"Updated {count} files.")