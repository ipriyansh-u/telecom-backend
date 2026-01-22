def handle_escalation(message: str, context: dict = None) -> dict:
    """Handle escalation requests."""
    return {
        "action": "escalate_to_agent",
        "requires_auth": False,
        "message": message
    }
