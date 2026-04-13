"""Application errors: HTTP-facing factories and private domain failures."""

from src.core.exceptions.domain import DomainErrors
from src.core.exceptions.http import HTTPErrors

__all__ = ["DomainErrors", "HTTPErrors"]
