"""
Sort primitives for list endpoints.

- ShortUrlSortBy names a stable, API-facing field for "my short URLs" lists.
- SortOrder is applied to that field; the persistence layer adds a deterministic
tie-breaker on primary key so pages do not shuffle when values repeat.

- To support a new column: extend both the Literal type below and the adapter's
column map (single place per layer).
"""

from typing import Literal, TypeAlias

ShortUrlSortBy: TypeAlias = Literal["created_at", "usage_count"]
SortOrder: TypeAlias = Literal["asc", "desc"]
