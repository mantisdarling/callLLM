"""Comprehensive offline unit test suite verifying tool execution, validation, and immutability."""

import pytest
from dataclasses import FrozenInstanceError
from types import MappingProxyType
from src.config import get_gemini_api_key
from src.database import CUSTOMERS, ORDERS
from src.tools import TOOL_REGISTRY, lookup_customer, lookup_order_status


def test_lookup_customer_valid_record():
    """Verify customer retrieval returns structured payload for known email."""
    result = lookup_customer("rohan.sharma@example.com")
    assert result["status"] == "success"
    assert result["customer_id"] == "CUST_1001"
    assert result["full_name"] == "Rohan Sharma"
    assert result["account_tier"] == "platinum"
    assert "ORD_8801" in result["order_ids"]
    assert "ORD_8802" in result["order_ids"]


def test_lookup_customer_whitespace_and_casing_normalization():
    """Verify input sanitization strips whitespace and normalizes uppercase characters."""
    result = lookup_customer("   ROHAN.SHARMA@EXAMPLE.COM   ")
    assert result["status"] == "success"
    assert result["customer_id"] == "CUST_1001"


def test_lookup_customer_missing_record():
    """Verify missing customer record yields deterministic not found message."""
    result = lookup_customer("nonexistent.user@example.com")
    assert result["status"] == "not_found"
    assert result["message"] == "No customer record matches the provided email"


def test_lookup_customer_malformed_email():
    """Verify malformed email strings fail schema validation cleanly."""
    result = lookup_customer("invalid_email_token")
    assert result["status"] == "error"
    assert "Input validation failure" in result["message"]


def test_lookup_order_status_valid_record():
    """Verify order retrieval returns expected shipping telemetry for known order."""
    result = lookup_order_status("A123")
    assert result["status"] == "success"
    assert result["order_id"] == "A123"
    assert result["shipping_status"] == "in_transit"
    assert result["carrier"] == "BlueDart Express"
    assert result["estimated_delivery"] == "November 25, 2026"
    assert "Mechanical Keyboard" in result["items"]


def test_lookup_order_status_normalization():
    """Verify order lookup normalizes lowercase casing and surrounding whitespace."""
    result = lookup_order_status("   a123   ")
    assert result["status"] == "success"
    assert result["order_id"] == "A123"


def test_lookup_order_status_missing_record():
    """Verify unknown order identifier yields deterministic not found response."""
    result = lookup_order_status("Z999")
    assert result["status"] == "not_found"
    assert result["message"] == "No order record matches the provided identifier"


def test_lookup_order_status_malformed_identifier():
    """Verify malformed order identifiers trigger schema validation rejection."""
    result = lookup_order_status("!!")
    assert result["status"] == "error"
    assert "Input validation failure" in result["message"]


def test_tool_registry_structure_and_dispatch():
    """Verify tool registry contains registered functions and enforces read only mapping."""
    assert isinstance(TOOL_REGISTRY, MappingProxyType)
    assert "lookup_customer" in TOOL_REGISTRY
    assert "lookup_order_status" in TOOL_REGISTRY
    assert TOOL_REGISTRY["lookup_customer"] == lookup_customer
    assert TOOL_REGISTRY["lookup_order_status"] == lookup_order_status

    with pytest.raises(TypeError):
        TOOL_REGISTRY["arbitrary_key"] = lambda: None


def test_database_immutability_guarantees():
    """Verify MappingProxyType prevents runtime modification of mock database state."""
    with pytest.raises(TypeError):
        CUSTOMERS["hacker@example.com"] = None

    with pytest.raises(TypeError):
        ORDERS["FAKE_ORDER"] = None

    customer_record = CUSTOMERS["rohan.sharma@example.com"]
    with pytest.raises(FrozenInstanceError):
        customer_record.full_name = "Modified Name"

    order_record = ORDERS["A123"]
    with pytest.raises(FrozenInstanceError):
        order_record.status = "tampered"


def test_config_validation_guards(monkeypatch):
    """Verify secret management rejects empty, missing, or placeholder credentials."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="not configured"):
        get_gemini_api_key()

    monkeypatch.setenv("GEMINI_API_KEY", "   ")
    with pytest.raises(RuntimeError, match="whitespace"):
        get_gemini_api_key()

    monkeypatch.setenv("GEMINI_API_KEY", "your_api_key_here")
    with pytest.raises(RuntimeError, match="placeholder"):
        get_gemini_api_key()

    monkeypatch.setenv("GEMINI_API_KEY", "valid_secret_token_12345")
    assert get_gemini_api_key() == "valid_secret_token_12345"
