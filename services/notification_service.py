import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def send_email_notification(self, recipient_email: str, subject: str, body: str) -> bool:
        """Simulates sending an email notification to candidates or recruiters."""
        logger.info(f"--- [Notification Sent] ---")
        logger.info(f"To: {recipient_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body:\n{body}")
        logger.info(f"---------------------------")
        return True
