"""Define validated tools and their Gemini function declarations."""

import re
from collections.abc import Callable
from types import MappingProxyType

from google.genai import types
from pydantic import BaseModel, Field, ValidationError, field_validator

from src.database import CUSTOMERS, ORDERS


class CustomerLookupInput(BaseModel):
    email: str = Field(min_length=5, max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized) is None:
            raise ValueError("Invalid email format")
        return normalized


class OrderLookupInput(BaseModel):
    order_id: str = Field(min_length=3, max_length=32)

    @field_validator("order_id")
    @classmethod
    def normalize_order_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        if re.fullmatch(r"[A-Z0-9]+(?:_[A-Z0-9]+)*", normalized) is None:
            raise ValueError("Invalid order ID format")
        return normalized


def lookup_customer(email: str) -> dict[str, object]:
    """Look up a customer by email and return their order IDs."""
    try:
        validated = CustomerLookupInput(email=email)
    except ValidationError:
        return {"status": "error", "message": "Invalid email format"}

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


def lookup_order_status(order_id: str) -> dict[str, object]:
    """Look up the current shipping status of an order by its ID."""
    try:
        validated = OrderLookupInput(order_id=order_id)
    except ValidationError:
        return {"status": "error", "message": "Invalid order ID format"}

    record = ORDERS.get(validated.order_id)
    if record is None:
        return {
            "status": "not_found",
            "message": "No order record matches the provided identifier",
        }

    return {
        "status": "success",
        "order_id": record.order_id,
        "shipping_status": record.status,
        "carrier": record.carrier,
        "estimated_delivery": record.estimated_delivery,
        "items": list(record.items),
    }


CUSTOMER_TOOL_DECLARATION = types.FunctionDeclaration(
    name="lookup_customer",
    description="Retrieve account profile and order identifiers for a customer using their registered email address",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "email": types.Schema(
                type=types.Type.STRING,
                description="The registered email address of the customer, for example rohan.sharma@example.com",
            ),
        },
        required=["email"],
    ),
)

ORDER_TOOL_DECLARATION = types.FunctionDeclaration(
    name="lookup_order_status",
    description="Retrieve shipping status, logistics carrier, and estimated delivery date for an order using its identifier",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "order_id": types.Schema(
                type=types.Type.STRING,
                description="The unique order identifier, for example A123 or ORD_8801",
            ),
        },
        required=["order_id"],
    ),
)

GEMINI_TOOLS = [
    types.Tool(
        function_declarations=[
            CUSTOMER_TOOL_DECLARATION,
            ORDER_TOOL_DECLARATION,
        ]
    )
]

_TOOL_REGISTRY_MAP: dict[str, Callable[..., dict[str, object]]] = {
    "lookup_customer": lookup_customer,
    "lookup_order_status": lookup_order_status,
}
TOOL_REGISTRY = MappingProxyType(_TOOL_REGISTRY_MAP)
