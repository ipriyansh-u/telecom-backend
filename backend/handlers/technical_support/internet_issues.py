def handle_internet_issues(message: str, context: dict = None) -> dict:
    """Handle internet connectivity issues."""
    return {
        "action": "troubleshoot_internet",
        "requires_auth": False,
        "message": message
    }
