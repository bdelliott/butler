import logging

from django.http import HttpResponse

import sync
from sync.models import Show, SyncJob, WishKeyword
from sync import queue

logger = logging.getLogger(__name__)

def job(request):
    """Run a tivo sync job"""
    if sync.sync_in_progress():
        # unfinished
        msg = "Previous job started not yet finished."
        logger.info(msg)
        return HttpResponse(content=msg)

    # kick off a new job
    job = SyncJob()
    job.save()

    # download show list:
    shows = sync.get_shows()
    logger.info("Number of shows on TiVo: %d" % len(shows))

    # prune list to new things to download:
    shows = queue.update(job, shows)
    logger.info("Number of shows added to queue: %d" % len(shows))

    # tag job as complete
    job.end = datetime.datetime.now()
    job.save()

    # process download queue
    #_process_download_queue()


def _process_download_queue():
    """download and decode video files"""

    pass
    #todos = TodoItem.objects.filter(not done items)
    # Download MPEG PS file:
    #net.tivoget(        

    # TODO decrypt.

    # TODO add to library
