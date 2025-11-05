"""
Rate limiting decorators and utilities
"""
from functools import wraps
from flask import request, jsonify
from flask_login import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

def get_rate_limit_key():
    """Get rate limit key based on user ID or IP address"""
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    return get_remote_address()

# Rate limit decorators
def rate_limit_auth():
    """Rate limit for authentication endpoints"""
    return "5 per minute"

def rate_limit_crud():
    """Rate limit for CRUD operations"""
    return "100 per hour"

def rate_limit_search():
    """Rate limit for search operations"""
    return "30 per minute"

def rate_limit_import():
    """Rate limit for data import"""
    return "10 per hour"

def rate_limit_api():
    """Rate limit for API endpoints"""
    return "1000 per hour"

