import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_otp_email(email: str, otp: str) -> bool:
    """Send the OTP code to the given email. Returns True on success."""
    subject = "Your verification code"
    message = f"Your verification code is: {otp}\nThis code expires in 5 minutes."
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send OTP email")
        return False

