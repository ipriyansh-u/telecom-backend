def handle_complaint(message: str, context: dict = None) -> dict:
    """Handle complaint registration requests."""
    return {
        "action": "register_complaint",
        "requires_auth": False,
        "message": message
    }
