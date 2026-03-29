"""Vercel serverless function entry point — wraps the Flask app."""
import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
