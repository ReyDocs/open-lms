import bleach


ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li", "ol", "strong", "ul",
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr", "span", "table", "tbody", "tr", "td", "th",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "span": ["class"],
}


def sanitize_rich_text(content: str) -> str:
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
