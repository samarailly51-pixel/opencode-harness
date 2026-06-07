def normalize_title(text: str) -> str:
    return text.lower()


def slugify(text: str) -> str:
    return text.replace(" ", "_")
