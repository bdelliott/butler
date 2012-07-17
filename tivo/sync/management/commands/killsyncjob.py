import datetime
import logging

from django.core.management.base import NoArgsCommand, CommandError

import sync
from sync import models

logger = logging.getLogger(__name__)

class Command(NoArgsCommand):
    help = "Tag dangling old sync jobs as complete."

    def handle_noargs(self, **options):
        # get hanging jobs:
        jobs = models.SyncJob.objects.filter(end__isnull=True)

        # tag each as complete:
        for job in jobs:
            logger.info("Completing job %d, started at %s" % (job.id,
                job.start))
            job.end = datetime.datetime.now()
            job.save()
