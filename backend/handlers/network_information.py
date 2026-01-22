def handle_network_info(message: str, context: dict = None) -> dict:
    """Handle network information requests."""
    return {
        "action": "network_info",
        "requires_auth": False,
        "message": message
    }
