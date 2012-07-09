import logging

from django.http import HttpResponse

from sync import get_shows
from sync.models import Show, SyncJob

logger = logging.getLogger(__name__)

def job(request):
    """Run a tivo sync job"""
        
    if _sync_in_progress():
        # unfinished
        msg = "Previous job started not yet finished."
        logger.info(msg)
        return HttpResponse(content=msg)

    # kick off a new job
    job = SyncJob()
    job.save()

    # download show list:
    shows = get_shows()

    # update m2m relationships
    _update_show_models(job, shows)

    # check which shows have already been downloaded & decoded

    # download missing shows.

def _get_show_model(show):
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

def _sync_in_progress():
    """check on status of the last, possibly unfinished job"""
    try:
        job = SyncJob.objects.latest('start')
        return not job.end
    except SyncJob.DoesNotExist:
        return False

def _update_show_models(job, shows):
    """Create shows and update m2m relationship with jobs"""
    show_models = []

    for show in shows:
        show_model = _get_show_model(show)

        # tag show model with the new job:
        show_model.jobs.add(job)
        show_models.append(show_model)

    return show_models
