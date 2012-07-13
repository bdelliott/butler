import datetime
import logging

from django.http import HttpResponse

import sync
from sync.models import Show, SyncJob, WishKeyword
from sync import queue
from sync import showfilter

logger = logging.getLogger(__name__)

def job(request):
    """Run a tivo sync job"""
    job = sync.latest_job()
    if job and not job.end:
        # unfinished
        msg = "Previous job %d started at %s, but not yet finished." % (job.id,
                job.start)
        logger.info(msg)
        return HttpResponse(content=msg)

    # kick off a new job
    job = SyncJob()
    job.save()
    try:
        logger.info("Starting sync job %d at %s" % (job.id, job.start))

        # download show list:
        shows = sync.get_shows()
        num_tivo_shows = len(shows)
        logger.info("Number of shows on TiVo: %d" % num_tivo_shows)

        # prune list to new things to download:
        shows = showfilter.update(job, shows)
        logger.info("Number of shows added to queue: %d" % len(shows))

        msg = "Sync job %d completed.\n" % job.id
        msg += "  %d shows scanned on TiVo.\n" % num_tivo_shows
        msg += "  %d shows added to the queue." % len(shows)
        return HttpResponse(content=msg, mimetype="text/plain")

    finally:
        # tag job as complete
        job.end = datetime.datetime.now()
        job.save()

def process_queue(request):
    """Process queue of shows that need downloading, decoding, etc."""

    items = queue.get_todo_list()
    logger.info("Processing queue of %d items" % len(items))

    for item in items:
        logger.info("Processing show '%s'" % item.show)
        queue.process(item)

    msg = "Processing complete."
    return HttpResponse(content=msg, mimetype="text/plain")

