import markdown as md

_markdown = md.Markdown(
    extensions=[
        "extra",
        "toc",
        "sane_lists",
        "tables",
        "fenced_code",
        "nl2br",
    ],
    output_format="html5",
)


def render_markdown(text: str) -> str:
    """Render Markdown to HTML.

    Content is written by staff only, so we trust the input and skip
    HTML sanitization (bleach double-encodes entities in code blocks).
    """
    if not text:
        return ""
    _markdown.reset()
    return _markdown.convert(text)
