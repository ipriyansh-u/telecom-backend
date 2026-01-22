def handle_feedback(message: str, context: dict = None) -> dict:
    """Handle feedback requests."""
    return {
        "action": "collect_feedback",
        "requires_auth": False,
        "message": message
    }
