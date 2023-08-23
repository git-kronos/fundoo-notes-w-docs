from threading import Thread

from django.core.mail import send_mail


class SendEmailThread(Thread):
    """Execute `send_mail()` in a separate thread to avoid latency in API response"""

    def __init__(
            self,
            recipient: str,
            msg: str | None = None,
            html_content: str | None = None,
    ):
        self.msg = msg
        self.recipient = recipient
        self.html_content = html_content
        super().__init__()

    def run(self) -> None:
        send_mail(
            subject="email checking",
            message=self.msg,
            from_email=None,
            recipient_list=[self.recipient],
            html_message=self.html_content,
        )
