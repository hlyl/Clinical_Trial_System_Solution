"""Pagination utilities for list endpoints."""

from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams:
    """Query parameters for pagination."""

    def __init__(
        self,
        limit: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
        offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    ):
        self.limit = limit
        self.offset = offset


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")

    @property
    def has_more(self) -> bool:
        """Check if there are more items available."""
        return self.offset + self.limit < self.total

    @property
    def page(self) -> int:
        """Current page number (1-based)."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 1
