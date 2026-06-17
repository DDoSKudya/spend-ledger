#!/usr/bin/env python3
"""Ensure each service implements operations declared in OpenAPI contracts."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

SERVICE_SPECS: list[tuple[str, str, str, bool]] = [
    ("auth", "services/auth", "contracts/auth-v1.yaml", True),
    ("ledger", "services/ledger", "contracts/ledger-v1.yaml", True),
    ("export", "services/export", "contracts/export-v1.yaml", True),
    ("bff", "services/bff", "contracts/bff-v1.yaml", False),
]

HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})

OPENAPI_EXPORT_SCRIPT = """
import json
import os
import re

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET", "test_jwt_secret_min_32_chars_for_contracts")
os.environ.setdefault(
    "AUTH_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/auth_test",
)
os.environ.setdefault(
    "LEDGER_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/ledger_test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("EXPORT_FILES_DIR", "/tmp/exports")

from app.main import app

def normalize(path: str) -> str:
    normalized = path.rstrip("/") or "/"
    return re.sub(r"\\{[^}]+\\}", "{id}", normalized)

operations = []
for path, path_item in app.openapi().get("paths", {}).items():
    normalized = normalize(path)
    for method, operation in path_item.items():
        if method.lower() not in {"get", "post", "put", "patch", "delete"}:
            continue
        operations.append(
            {
                "method": method.upper(),
                "path": normalized,
                "responses": sorted(str(code) for code in operation.get("responses", {})),
                "request_body": "requestBody" in operation,
            }
        )

print(json.dumps(operations))
"""


@dataclass(frozen=True)
class OperationSpec:
    method: str
    path: str
    responses: frozenset[str]
    request_body: bool


def _normalize_path(path: str) -> str:
    normalized = path.rstrip("/") or "/"
    return re.sub(r"\{[^}]+\}", "{id}", normalized)


def _load_contract_operations(contract_path: Path) -> dict[tuple[str, str], OperationSpec]:
    document = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    operations: dict[tuple[str, str], OperationSpec] = {}
    for path, path_item in document.get("paths", {}).items():
        normalized = _normalize_path(path)
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            key = (method.upper(), normalized)
            operations[key] = OperationSpec(
                method=key[0],
                path=key[1],
                responses=frozenset(str(code) for code in operation.get("responses", {})),
                request_body="requestBody" in operation,
            )
    return operations


def _load_app_operations(service_dir: Path) -> dict[tuple[str, str], OperationSpec]:
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    result = subprocess.run(
        ["uv", "run", "python", "-c", OPENAPI_EXPORT_SCRIPT],
        cwd=service_dir,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)

    operations: dict[tuple[str, str], OperationSpec] = {}
    for item in json.loads(result.stdout):
        key = (item["method"], item["path"])
        operations[key] = OperationSpec(
            method=key[0],
            path=key[1],
            responses=frozenset(item["responses"]),
            request_body=bool(item["request_body"]),
        )
    return operations


def _success_responses(responses: frozenset[str]) -> frozenset[str]:
    return frozenset(code for code in responses if code.startswith(("2", "3")))


def main() -> int:
    failures: list[str] = []

    for service_name, service_path, contract_path, check_details in SERVICE_SPECS:
        contract_file = ROOT / contract_path
        service_dir = ROOT / service_path
        expected = _load_contract_operations(contract_file)
        actual = _load_app_operations(service_dir)

        missing = sorted(set(expected) - set(actual))
        if missing:
            formatted = ", ".join(f"{method} {path}" for method, path in missing)
            failures.append(f"{service_name}: missing contract operations: {formatted}")
            continue

        if not check_details:
            continue

        for key, contract_op in expected.items():
            app_op = actual[key]
            missing_responses = sorted(
                _success_responses(contract_op.responses) - _success_responses(app_op.responses),
            )
            if missing_responses:
                failures.append(
                    f"{service_name}: {contract_op.method} {contract_op.path} "
                    f"missing success response codes: {', '.join(missing_responses)}",
                )
            if contract_op.request_body and not app_op.request_body:
                failures.append(
                    f"{service_name}: {contract_op.method} {contract_op.path} "
                    "missing requestBody in app OpenAPI",
                )

    if failures:
        print("OpenAPI contract validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("OpenAPI contract validation passed for auth, ledger, export, bff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
