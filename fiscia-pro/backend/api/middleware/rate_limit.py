"""Minimal plan-based rate limiting placeholder."""

from __future__ import annotations

from fastapi import Header


async def get_plan_name(x_plan: str | None = Header(default=None)) -> str:
    return (x_plan or "starter").lower()

