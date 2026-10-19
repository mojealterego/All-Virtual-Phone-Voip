"""Authentication is derived from server-managed secrets, never request fields."""
from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Principal:
    identity: str
    role: Literal["tenant", "carrier"]


class ApiCredentials:
    def __init__(self, tenants: dict[str, str], carriers: dict[str, str]):
        if not tenants or not carriers:
            raise ValueError("Tenant and carrier credentials must both be configured")
        all_secrets = [*tenants.values(), *carriers.values()]
        if any(len(secret.encode("utf-8")) < 32 for secret in all_secrets):
            raise ValueError("Each API key must contain at least 32 UTF-8 bytes")
        if len(set(all_secrets)) != len(all_secrets):
            raise ValueError("API keys must be unique across identities and roles")
        self._entries = (
            [(Principal(identity, "tenant"), secret) for identity, secret in tenants.items()]
            + [(Principal(identity, "carrier"), secret) for identity, secret in carriers.items()]
        )

    def resolve(self, bearer_token: str) -> Principal | None:
        match: Principal | None = None
        for principal, secret in self._entries:
            if hmac.compare_digest(bearer_token, secret):
                match = principal
        return match

    @classmethod
    def from_environment(cls) -> "ApiCredentials":
        value = os.environ.get("AVP_API_KEYS_JSON")
        if not value:
            raise ValueError("AVP_API_KEYS_JSON must be configured")
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                raise ValueError("credentials must be an object")
            tenants = parsed["tenants"]
            carriers = parsed["carriers"]
            if not isinstance(tenants, dict) or not isinstance(carriers, dict):
                raise ValueError("roles must map identities to secrets")
            if not all(
                isinstance(k, str) and k and isinstance(v, str)
                for pool in (tenants, carriers)
                for k, v in pool.items()
            ):
                raise ValueError("invalid identity or secret")
            return cls(tenants=tenants, carriers=carriers)
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid AVP_API_KEYS_JSON structure") from exc
