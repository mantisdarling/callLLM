"""Immutable backend data store encapsulating customer and order state."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Tuple


@dataclass(frozen=True)
class CustomerRecord:
    """Immutable data model representing customer entity state."""

    customer_id: str
    full_name: str
    account_tier: str
    order_ids: Tuple[str, ...]


@dataclass(frozen=True)
class OrderRecord:
    """Immutable data model representing order shipment state."""

    order_id: str
    status: str
    carrier: str
    estimated_delivery: str
    items: Tuple[str, ...]


_CUSTOMERS_STORE = {
    "rohan.sharma@example.com": CustomerRecord(
        customer_id="CUST_1001",
        full_name="Rohan Sharma",
        account_tier="platinum",
        order_ids=("ORD_8801", "ORD_8802"),
    ),
    "ananya.iyer@example.com": CustomerRecord(
        customer_id="CUST_1002",
        full_name="Ananya Iyer",
        account_tier="gold",
        order_ids=("A123",),
    ),
    "vikram.patel@example.com": CustomerRecord(
        customer_id="CUST_1003",
        full_name="Vikram Patel",
        account_tier="silver",
        order_ids=("ORD_8803", "ORD_8804"),
    ),
    "priya.nair@example.com": CustomerRecord(
        customer_id="CUST_1004",
        full_name="Priya Nair",
        account_tier="platinum",
        order_ids=("ORD_8805",),
    ),
    "arjun.mehta@example.com": CustomerRecord(
        customer_id="CUST_1005",
        full_name="Arjun Mehta",
        account_tier="bronze",
        order_ids=(),
    ),
}

_ORDERS_STORE = {
    "A123": OrderRecord(
        order_id="A123",
        status="in_transit",
        carrier="BlueDart Express",
        estimated_delivery="November 25, 2026",
        items=("Mechanical Keyboard", "USB C Hub"),
    ),
    "ORD_8801": OrderRecord(
        order_id="ORD_8801",
        status="in_transit",
        carrier="BlueDart Express",
        estimated_delivery="November 24, 2026",
        items=("Wireless Ergonomic Mouse",),
    ),
    "ORD_8802": OrderRecord(
        order_id="ORD_8802",
        status="delivered",
        carrier="Delhivery",
        estimated_delivery="November 20, 2026",
        items=("Noise Cancelling Headphones",),
    ),
    "ORD_8803": OrderRecord(
        order_id="ORD_8803",
        status="out_for_delivery",
        carrier="FedEx Ground",
        estimated_delivery="November 22, 2026",
        items=("4K Ultra HD Monitor",),
    ),
    "ORD_8804": OrderRecord(
        order_id="ORD_8804",
        status="processing",
        carrier="DHL Express",
        estimated_delivery="November 28, 2026",
        items=("Ergonomic Office Chair",),
    ),
    "ORD_8805": OrderRecord(
        order_id="ORD_8805",
        status="delivered",
        carrier="BlueDart Express",
        estimated_delivery="November 18, 2026",
        items=("Desk Mat", "Vertical Mouse"),
    ),
}

CUSTOMERS = MappingProxyType(_CUSTOMERS_STORE)
ORDERS = MappingProxyType(_ORDERS_STORE)
