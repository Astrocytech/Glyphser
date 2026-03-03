"""Public runtime service wrappers.

This module provides the stable facade for runtime operations.
"""

from runtime.glyphser.api.runtime_api import RuntimeApiConfig
from runtime.glyphser.api.runtime_api import RuntimeApiService as RuntimeService

__all__ = ["RuntimeApiConfig", "RuntimeService"]
