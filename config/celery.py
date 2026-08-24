from __future__ import annotations

import logging
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

logger = logging.getLogger(__name__)

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.debug("Celery debug task request: %r", self.request)
