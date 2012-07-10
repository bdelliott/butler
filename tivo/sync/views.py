import logging

from django.http import HttpResponse

import sync
from sync.models import Show, SyncJob

logger = logging.getLogger(__name__)

def job(request):
    """Run a tivo sync job"""
    if False:    
    #if _sync_in_progress():
        # unfinished
        msg = "Previous job started not yet finished."
        logger.info(msg)
        return HttpResponse(content=msg)

    # kick off a new job
    job = SyncJob()
    job.save()

    # download show list:
    shows = sync.get_shows()

    # update m2m relationships
    shows = _update_show_models(job, shows)  # gets list of Show models.

    # check which shows have already been downloaded & decoded
    _update_download_queue(shows)

    # process download queue
    _process_download_queue()

def _get_show_model(show):
    # sanity check some data:

    try:
        return Show.objects.get(title=show['title'], date=show['date'],
            url=show['link_url'])
    except Show.DoesNotExist:
        model = Show()
        model.title = show['title']
        model.description = show.get('description', "")
        model.date = show['date']
        model.duration = show['duration']
        model.url = show['link_url']
        model.size = show['size']
        model.save()

    return model

def _on_wishlist(shows):
    """check if there's a matching wishlist keyword entry for these shows"""

    wishes = WishKeyword.objects.all()
    
    # naive search.  i'm tired and half drunk
    wshows = []

    def match(title, keyword):
        if not keyword:
            return True
        keyword = keyword.lower()
        return title.find(keyword) != -1

    for show in shows:
        title = show.title.lower()

        for wish in wishes:
            if not match(title, wish.keyword1):
                continue
            if not match(title, wish.keyword2):
                continue
            if not match(title, wish.keyword2):
                continue
            wshows.add(show)
            break
    return wshows

def _process_download_queue():
    """download and decode video files"""

    pass
    #todos = TodoItem.objects.filter(not done items)
    # Download MPEG PS file:
    #net.tivoget(        

    # TODO decrypt.

    # TODO add to library

def _sync_in_progress():
    """check on status of the last, possibly unfinished job"""
    try:
        job = SyncJob.objects.latest('start')
        return not job.end
    except SyncJob.DoesNotExist:
        return False

def _update_download_queue(shows):
    """add missing shows to the download queue"""
   
    shows = _prune_by_wishlist(shows)
    # slow, but simple:
    for show in shows:
        try:
            TodoItem.objects.get(show=show)
            # already on the queue list, do nothing.
        except TodoItem.DoesNotExist:
            todo_item = TodoItem()
            todo_item.show = show
            todo_item.save()

def _update_show_models(job, shows):
    """Create shows and update m2m relationship with jobs"""
    show_models = []

    for show in shows:
        show_model = _get_show_model(show)

        # tag show model with the new job:
        show_model.jobs.add(job)
        show_models.append(show_model)

    return show_models

