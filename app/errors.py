"""Application-level exception types for user-facing API failures."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base exception carrying an HTTP status, stable code, and safe details."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class BadRequestError(ApplicationError):
    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(
            message,
            code="bad_request",
            status_code=400,
            details=details,
        )


class NotFoundError(ApplicationError):
    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(
            message,
            code="not_found",
            status_code=404,
            details=details,
        )


class ConflictError(ApplicationError):
    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(
            message,
            code="conflict",
            status_code=409,
            details=details,
        )
