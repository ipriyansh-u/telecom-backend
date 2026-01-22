def handle_account_info(message: str, context: dict = None) -> dict:
    """Handle account information requests."""
    return {
        "action": "fetch_account_info",
        "requires_auth": True,
        "message": message
    }
