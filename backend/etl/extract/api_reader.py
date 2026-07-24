from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


@dataclass(frozen=True)
class APIConfig:
    base_url: str
    token: str | None = None
    timeout_seconds: int = 30


class APIReader:
    """Extractor cho REST API, hỗ trợ JSON và pagination đơn giản."""

    def __init__(self, config: APIConfig):
        self.config = config

    def request_json(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        query = f"?{parse.urlencode(params)}" if params else ""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}{query}"

        request_headers = {"Accept": "application/json"}
        if self.config.token:
            request_headers["Authorization"] = f"Bearer {self.config.token}"
        if headers:
            request_headers.update(headers)

        data = None
        if payload is not None:
            request_headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url=url,
            method=method.upper(),
            headers=request_headers,
            data=data,
        )

        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API error {exc.code} for {url}: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Cannot reach API {url}: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON response from {url}") from exc

    def fetch_paginated_items(
        self,
        endpoint: str,
        item_key: str = "items",
        page_param: str = "page",
        start_page: int = 1,
        max_pages: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        current_page = start_page
        collected: list[dict[str, Any]] = []
        base_params = dict(params or {})

        while True:
            page_params = {**base_params, page_param: current_page}
            payload = self.request_json("GET", endpoint, params=page_params)

            if isinstance(payload, dict):
                items = payload.get(item_key, [])
            else:
                items = payload

            if not isinstance(items, list):
                raise ValueError(f"Expected list at key '{item_key}', received: {type(items)!r}")

            if not items:
                break

            collected.extend(items)

            current_page += 1
            if max_pages is not None and (current_page - start_page) >= max_pages:
                break

        return collected