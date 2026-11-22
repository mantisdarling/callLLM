"""Schema validated tool layer implementing deterministic dispatch and input validation."""

from types import MappingProxyType
from typing import Any, Callable, Dict
from google.genai import types
from pydantic import BaseModel, Field, ValidationError, field_validator
from src.database import CUSTOMERS, ORDERS


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


class OrderLookupInput(BaseModel):
    """Schema validation for order identifier lookup input."""

    order_id: str = Field(min_length=3, max_length=32)

    @field_validator("order_id")
    @classmethod
    def sanitize_order_id(cls, value: str):
        """Strip whitespace and enforce uppercase normalization for database query alignment."""
        sanitized = value.strip().upper()
        if not sanitized.isalnum() and "_" not in sanitized:
            raise ValueError("Malformed order identifier format")
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


def lookup_order_status(order_id: str):
    """Retrieve fulfillment lifecycle state and logistics information for an order.

    Validates input through OrderLookupInput schema, normalizes identifier casing,
    and queries immutable order storage, returning verified shipment telemetry
    grounded in immutable backend state.
    """
    try:
        validated = OrderLookupInput(order_id=order_id)
    except ValidationError as error:
        return {"status": "error", "message": f"Input validation failure: {error}"}

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

_TOOL_REGISTRY_MAP: Dict[str, Callable[..., Dict[str, Any]]] = {
    "lookup_customer": lookup_customer,
    "lookup_order_status": lookup_order_status,
}

TOOL_REGISTRY: MappingProxyType[str, Callable[..., Dict[str, Any]]] = MappingProxyType(
    _TOOL_REGISTRY_MAP
)
