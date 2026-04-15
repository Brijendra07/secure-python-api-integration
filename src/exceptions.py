class APIIntegrationError(Exception):
    """Base exception for integration failures."""


class AuthenticationError(APIIntegrationError):
    """Raised when authentication fails."""


class RequestExecutionError(APIIntegrationError):
    """Raised when an authenticated API request fails."""
