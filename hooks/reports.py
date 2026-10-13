"""MkDocs hook: adapt the report Markdown (written for GitHub) for the site.

- Links to files that are not published on the site (raw data, scripts,
  SOURCES.md) are rewritten to point at the file on GitHub.
- The "What changed in the … edition" blockquote becomes an admonition.
- Chart images get lazy loading.
- Each report ends with a pointer to its data and code on GitHub.

The report files themselves are not modified.
"""
import re

REPO = "https://github.com/mihaigociu/economie"
# site-src/reports/<slug> -> repo folder
FOLDERS = {
    "romania": "romania",
    "greece": "greece",
    "it-romania": "it-romania",
    "china": "china-industry",
}

LINK = re.compile(r"(?<!!)\]\((?!https?://|#|mailto:|charts/)([^)\s]+)\)")
IMAGE = re.compile(r"^(!\[[^\]]*\]\(charts/[^)]+\))\s*$", re.M)
CHANGED_BOX = re.compile(
    r"^> \*\*(What changed in the [^*]+)\*\*\n((?:>.*\n?)+)", re.M)


def _report_folder(page):
    parts = page.file.src_uri.split("/")
    if len(parts) == 3 and parts[0] == "reports" and parts[2] == "report.md":
        return FOLDERS.get(parts[1])
    return None


def _box_to_admonition(match):
    title, body = match.group(1), match.group(2)
    lines = [re.sub(r"^> ?", "", line) for line in body.rstrip("\n").split("\n")]
    indented = "\n".join(("    " + line) if line.strip() else "" for line in lines)
    return f'!!! info "{title}"\n\n{indented}\n'


def on_page_markdown(markdown, page, config, files):
    folder = _report_folder(page)
    if folder is None:
        return markdown
    base = f"{REPO}/blob/main/{folder}"
    markdown = LINK.sub(lambda m: f"]({base}/{m.group(1)})", markdown)
    markdown = CHANGED_BOX.sub(_box_to_admonition, markdown, count=1)
    markdown = IMAGE.sub(r"\1{ loading=lazy }", markdown)
    markdown = markdown.rstrip() + (
        "\n\n---\n\n"
        f"*The raw data (CSV, each with its source and retrieval date) and "
        f"the Python scripts that produce every chart in this report are on "
        f"[GitHub]({REPO}/tree/main/{folder}).*\n"
    )
    return markdown
