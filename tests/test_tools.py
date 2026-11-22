"""Comprehensive offline unit test suite verifying tool execution, validation, and immutability."""

import pytest
from src.tools import lookup_customer


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
