from __future__ import annotations

from threading import Lock


class TokenBlacklistService:
    def __init__(self) -> None:
        self._revoked_jti: set[str] = set()
        self._lock = Lock()

    def revoke(self, jti: str | None) -> None:
        if not jti:
            return

        with self._lock:
            self._revoked_jti.add(jti)

    def is_revoked(self, jti: str | None) -> bool:
        if not jti:
            return False

        with self._lock:
            return jti in self._revoked_jti


blacklist_service = TokenBlacklistService()
