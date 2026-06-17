from math import ceil

from pydantic import BaseModel


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


def compute_pages(total: int, size: int) -> int:
    return 0 if total == 0 else ceil(total / size)


def build_page[T](items: list[T], *, total: int, page: int, size: int) -> Page[T]:
    return Page(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=compute_pages(total, size),
    )
