def handle_telecom_knowledge(message: str, context: dict = None) -> dict:
    """Handle telecom knowledge requests."""
    return {
        "action": "telecom_knowledge",
        "requires_auth": False,
        "message": message
    }
