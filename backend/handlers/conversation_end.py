def handle_conversation_end(message: str, context: dict = None) -> dict:
    """Handle conversation end requests."""
    return {
        "action": "end_conversation",
        "requires_auth": False,
        "message": message
    }
