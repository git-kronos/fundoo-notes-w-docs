import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("fundoo_note")
app.conf.broker_url = "redis://localhost:6379/0"  # type: ignore
app.conf.broker_connection_retry_on_startup = True

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'apps.user.tasks.thought_of_the_day',
#         'schedule': crontab(minute='*/1'),
#         'args': ()
#     },
# }


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
