from celery import shared_task
from django.core.mail import send_mail
from django_celery_beat.models import PeriodicTask  # noqa


@shared_task
def send_user_verification_email_task(recipient: str, msg: str | None = None, html_content: str | None = None):
    send_mail(
        subject="email checking",
        message=msg,  # type: ignore
        from_email=None,
        recipient_list=[recipient],
        html_message=html_content,
    )
    return True


@shared_task
def thought_of_the_day():
    import faker
    fake = faker.Faker()
    print('=============================')
    print(fake.sentence())
    print('=============================')
    return 'ok'
