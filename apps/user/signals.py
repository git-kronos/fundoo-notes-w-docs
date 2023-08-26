from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from apps.user.tasks import send_user_verification_email_task  # noqa
from apps.utils import JWT

User = get_user_model()


@receiver(signal=post_save, sender=User)
def verify_email_id_on_registration(instance: User, **kwargs):  # type: ignore
    if settings.EMAIL_ACTIVE:
        recipient = instance.email
        token_payload = {
            "body": {"email": recipient},
            "aud": JWT.Aud.VERIFY,
            "exp": datetime.now() + timedelta(minutes=30),
        }
        context = {
            "email": recipient,
            "url": settings.BASE_URI + reverse("user:verify", kwargs={"token": JWT.encode(**token_payload)}),
        }
        html_content = render_to_string("components/mail.html", context=context)
        # thread = SendEmailThread(recipient=instance.email, html_content=html_content)
        # thread.start()
        send_user_verification_email_task.delay(
            recipient=instance.email,
            html_content=html_content,
        )
