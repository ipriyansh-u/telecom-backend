def handle_plan_management(message: str, context: dict = None) -> dict:
    """Handle plan management requests."""
    return {
        "action": "manage_plan",
        "requires_auth": True,
        "message": message
    }
