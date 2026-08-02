DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def resolve_page(page_size: int, page_token: str) -> tuple[int, int]:
    size = page_size or DEFAULT_PAGE_SIZE
    if size <= 0:
        raise ValueError("page_size must be a positive integer")
    if size > MAX_PAGE_SIZE:
        size = MAX_PAGE_SIZE

    offset = 0
    token = (page_token or "").strip()
    if token:
        try:
            offset = int(token)
        except ValueError as exc:
            raise ValueError("invalid page_token") from exc
        if offset < 0:
            raise ValueError("invalid page_token")
    return size, offset


def next_page_token(offset: int, size: int, rows: list) -> tuple[list, str]:
    if len(rows) > size:
        return rows[:size], str(offset + size)
    return rows, ""
