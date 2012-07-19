import datetime
import logging

from django.core.management.base import NoArgsCommand, CommandError

import sync
from sync import models
from sync import queue
from sync import showfilter

logger = logging.getLogger(__name__)

class Command(NoArgsCommand):
    """If no sync jobs are in progress, sync with Tivo and then process any
    items in the TODO queue
    """
    help = "Sync with TiVo.  Download, and re-encode shows as necessary."

    def handle_noargs(self, **options):
        self.job()

    def job(self):
        """Confirm no sync job is running, otherwise kick off a new one"""

        job = sync.latest_job()
        if job and not job.end:
            # unfinished
            msg = "Previous job %d started at %s, but not yet finished." % (job.id,
                            job.start)
            logger.info(msg)
            raise CommandError(msg)

        else:
            job = models.SyncJob()
            job.save()
            try:
                self.new_job(job)
            finally:
                # tag job as complete
                logger.info("Finishing job %d" % job.id)
                job.end = datetime.datetime.now()
                job.save()

    def new_job(self, job):
        """kick off a new job"""

        logger.info("Starting sync job %d at %s" % (job.id, job.start))

        # download show list:
        shows = sync.get_shows()
        num_tivo_shows = len(shows)
        logger.info("Number of shows on TiVo: %d" % num_tivo_shows)

        # prune list to new things to download:
        shows = showfilter.update(job, shows)
        logger.info("Number of shows added to queue: %d" % len(shows))

        # kick off queue processing in the background:
        num_processed = self.process_queue(job)

        msg = "Sync job %d:\n" % job.id
        msg += "  %d shows scanned on TiVo.\n" % num_tivo_shows
        msg += "  %d shows added to the queue.\n\n" % len(shows)
        msg += "  %d shows processed from the queue.\n\n" % num_processed
        logger.info(msg)

    def process_queue(self, job):
        """Process items in queue and then tag the job as complete.  Will take a
        *very* *long* *time*
        """
        items = queue.get_todo_list()
        logger.info("Processing queue of %d items" % len(items))

        for item in items:
            logger.info("Processing show '%s'" % item.show)
            queue.process(item)

        return len(items)
