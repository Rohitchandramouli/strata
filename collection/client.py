"""
It is a thin, dumb HTTP transport layer.
It knows nothing about repositories, rate limits, streams, or GraphQL semantics.
It just sends POST requests and returns responses.
"""

import time
from typing import Any, Optional

import httpx

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

class GitHubAPIError(Exception):
    pass

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.session = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=5.0)  # Set timeouts for requests
        )

    def send_query(self, query: str, variables: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Send a GraphQL query to the GitHub API and return the response data.
        """
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        MAX_ATTEMPTS = 4                                        # 1 initial + 3 retries
        BACKOFF_DELAYS = [30, 60, 120]

        for attempt in range(MAX_ATTEMPTS):
            try:
                response = self.session.post(GITHUB_GRAPHQL_URL, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status in (500, 502, 503) and attempt < len(BACKOFF_DELAYS):
                    time.sleep(BACKOFF_DELAYS[attempt])
                    continue
                raise GitHubAPIError(f"Non-recoverable HTTP {status}: {e}") from e

            except (httpx.TimeoutException, httpx.TransportError) as e:
                # network hiccup — recoverable
                if attempt < len(BACKOFF_DELAYS):
                    time.sleep(BACKOFF_DELAYS[attempt])
                    continue
                raise GitHubAPIError(f"Network failure after retries: {e}") from e

            body: dict[str, Any] = response.json()
            if "errors" in body:
                raise GitHubAPIError(f"GraphQL error: {body['errors']}")

            # Every query we send requests a rateLimit block, so a well-formed response
            # must carry one. A null/missing rateLimit means a malformed or partial
            # response — treat it as non-recoverable rather than passing it downstream.
            data = body.get("data")
            if data is not None and data.get("rateLimit") is None:
                raise GitHubAPIError(f"Response missing rateLimit block: {body}")

            return body

        raise GitHubAPIError("unreachable: retry loop exited without returning")
