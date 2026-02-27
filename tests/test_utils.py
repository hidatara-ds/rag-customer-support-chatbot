"""
Tests for utility functions.
"""
import pytest
from app.utils import (
    is_order_status_query,
    extract_order_id,
    is_product_query,
    is_warranty_query,
    format_history_for_prompt
)


def test_is_order_status_query():
    """Test order status query detection"""
    assert is_order_status_query("where is my order") == True
    assert is_order_status_query("order status") == True
    assert is_order_status_query("check order #123") == True
    assert is_order_status_query("hello") == False


def test_extract_order_id():
    """Test order ID extraction"""
    assert extract_order_id("check order #123") == 123
    assert extract_order_id("order 456") == 456
    assert extract_order_id("where is my order") is None


def test_is_product_query():
    """Test product query detection"""
    assert is_product_query("what is espresso") == True
    assert is_product_query("tell me about latte") == True
    assert is_product_query("product information") == True
    assert is_product_query("hello") == False


def test_is_warranty_query():
    """Test warranty query detection"""
    assert is_warranty_query("warranty information") == True
    assert is_warranty_query("how to claim warranty") == True
    assert is_warranty_query("garansi") == True
    assert is_warranty_query("hello") == False


def test_format_history_for_prompt():
    """Test conversation history formatting"""
    # Mock conversation objects
    class MockConversation:
        def __init__(self, role, message):
            self.role = role
            self.message = message
    
    history = [
        MockConversation("user", "Hello"),
        MockConversation("assistant", "Hi there!"),
    ]
    
    result = format_history_for_prompt(history)
    assert "User: Hello" in result
    assert "Assistant: Hi there!" in result
