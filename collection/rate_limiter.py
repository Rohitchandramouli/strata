"""
It is a module that provides a rate limiter for controlling the rate of requests to a resource.
It watches the point budget and pauses collection when you're near empty.
It never asks GitHub for the budget — every response already carries a rateLimit block inside data, so the budget comes to it for free.
It absorbs each response's budget block, judges whether you're low, waits when told.
"""

import json
import os
from datetime import datetime, timezone
from time import sleep
from typing import Any

from collection.client import GitHubClient

VERIFICATION_QUERY = """
    query {
        rateLimit {
            remaining
            resetAt
        }
    }
"""

def log_to_jsonl(data: dict[str, Any], filename: str = "data/raw/rate_limit_log.jsonl") -> None:
    """
    Log data to a JSONL file.
    """

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")
        f.flush()

class RateLimiter:
    def __init__(self, client: GitHubClient, threshold: int = 200, cushion_time: int = 15) -> None:
        """
        Initialize the rate limiter.

        Args:
            client: The GitHub client instance.
            threshold: The rate limit threshold.
            cushion_time: The time to wait before the rate limit resets.
        """
        self.client = client
        self.threshold = threshold
        self.cushion_time = cushion_time
        self.remaining = 0
        self.reset_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update(self, response: dict[str, Any]) -> None:
        """
            Update the rate limiter from a response's rateLimit block.
            The client guarantees a well-formed rateLimit is present, so no null-guarding here.
        """
        rate_limit_info = response["data"]["rateLimit"]
        self.remaining = rate_limit_info["remaining"]
        self.reset_time = rate_limit_info["resetAt"]

    def is_budget_low(self) -> bool:
        """
        Check if the remaining budget is below the threshold.
        """
        return self.remaining < self.threshold

    def wait_for_reset(self) -> None:
        """
        Wait until the rate limit resets if the budget is low.
        Also logs the wait time to a JSONL file and performs verification query to ensure the budget has been restored.
        """
        while self.is_budget_low():
            reset_datetime = datetime.fromisoformat(self.reset_time.replace("Z", "+00:00"))
            wait_time = (reset_datetime - datetime.now(timezone.utc)).total_seconds() + self.cushion_time
            if wait_time <= 0:
                sleep(self.cushion_time)   # small floor — don't spin
                self.update(self.client.send_query(VERIFICATION_QUERY))
                continue
            log_to_jsonl({
                "event": "rate_limit_sleep",
                "logged_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "remaining": self.remaining,
                "reset_at": self.reset_time,
                "wait_seconds": round(wait_time, 1),
            })
            sleep(wait_time)
            self.update(self.client.send_query(VERIFICATION_QUERY))
