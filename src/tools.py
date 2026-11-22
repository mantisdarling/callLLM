"""Schema validated tool layer implementing deterministic dispatch and input validation."""

from typing import Any, Dict
from pydantic import BaseModel, Field, ValidationError, field_validator
from src.database import CUSTOMERS


class CustomerLookupInput(BaseModel):
    """Schema validation for customer email lookup input."""

    email: str = Field(min_length=5, max_length=254)

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, value: str):
        """Strip whitespace and enforce lowercase normalization for database query alignment."""
        sanitized = value.strip().lower()
        if "@" not in sanitized or "." not in sanitized:
            raise ValueError("Malformed email address format")
        return sanitized


def lookup_customer(email: str):
    """Retrieve customer account information and associated order references.

    Validates input through CustomerLookupInput schema, normalizes email casing,
    and queries immutable customer storage, returning structured entity details
    following Toolformer deterministic invocation principles.
    """
    try:
        validated = CustomerLookupInput(email=email)
    except ValidationError as error:
        return {"status": "error", "message": f"Input validation failure: {error}"}

    record = CUSTOMERS.get(validated.email)
    if record is None:
        return {
            "status": "not_found",
            "message": "No customer record matches the provided email",
        }

    return {
        "status": "success",
        "customer_id": record.customer_id,
        "full_name": record.full_name,
        "account_tier": record.account_tier,
        "order_ids": list(record.order_ids),
    }
