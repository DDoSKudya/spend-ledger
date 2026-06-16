from fastapi import APIRouter, Request

from app.clients.proxy import forward_to_ledger


def ledger_proxy_router(
    resource: str,
    *,
    item_methods: list[str],
) -> APIRouter:
    router = APIRouter(prefix=f"/api/v1/{resource}", tags=[resource])
    internal_prefix = f"/internal/v1/{resource}"

    @router.api_route("", methods=["GET", "POST"])
    async def collection(request: Request):
        return await forward_to_ledger(request, internal_prefix)

    @router.api_route("/{item_id}", methods=item_methods)
    async def item(request: Request, item_id: str):
        return await forward_to_ledger(request, f"{internal_prefix}/{item_id}")

    return router


categories_router = ledger_proxy_router("categories", item_methods=["GET", "PUT", "DELETE"])
tags_router = ledger_proxy_router("tags", item_methods=["GET", "PATCH", "DELETE"])
expenses_router = ledger_proxy_router("expenses", item_methods=["GET", "PUT", "DELETE"])
