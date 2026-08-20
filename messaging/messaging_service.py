from database.repositories import send_message, get_messages_by_application

class MessagingService:
    def post_message(self, application_id: int, sender_id: int, sender_role: str, message: str):
        """Sends a message from a candidate or recruiter on a job application."""
        if not message.strip():
            return None
        return send_message(application_id, sender_id, sender_role, message)

    def fetch_chat_history(self, application_id: int) -> list:
        """Retrieves history of messages exchange for an application."""
        return get_messages_by_application(application_id)
