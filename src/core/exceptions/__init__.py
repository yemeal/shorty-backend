"""Public error types: ``HTTPErrors`` for HTTP and ``DomainErrors`` inside services."""

from src.core.exceptions.domain import DomainErrors
from src.core.exceptions.http import HTTPErrors

__all__ = ["DomainErrors", "HTTPErrors"]
