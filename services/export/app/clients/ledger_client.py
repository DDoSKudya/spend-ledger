from collections.abc import Iterator
from typing import Any, TypedDict, cast
from uuid import UUID

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.jobs.schemas import ExportFilters

DEFAULT_PAGE_SIZE = 100


class ExpenseListPage(TypedDict):
    items: list[dict[str, Any]]
    pages: int


class LedgerClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def iter_expenses(
        self,
        user_id: UUID,
        filters: ExportFilters,
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
        request_id: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        page = 1
        headers = {"X-User-Id": str(user_id)}
        if request_id:
            headers["X-Request-Id"] = request_id

        while True:
            payload = self._fetch_page(filters, page=page, size=page_size, headers=headers)
            yield from payload["items"]
            if page >= payload["pages"]:
                break
            page += 1

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def _fetch_page(
        self,
        filters: ExportFilters,
        *,
        page: int,
        size: int,
        headers: dict[str, str],
    ) -> ExpenseListPage:
        response = self._client.get(
            "/internal/v1/expenses",
            params=filters.to_query_params(page=page, size=size),
            headers=headers,
        )
        response.raise_for_status()
        return cast(ExpenseListPage, response.json())
