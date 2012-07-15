import logging

from sync import models

logger = logging.getLogger(__name__)

def update(job, shows):
    # update m2m relationships
    shows = _update_show_models(job, shows)  # gets list of Show models.
    
    logger.debug("Got %d show models" % len(shows))

    # prune to things on the "wish list":
    shows = _on_wishlist(shows)
    logger.info("%d shows on the wishlist" % len(shows))

    # add any new shows to the queue for processing:
    return _update_download_queue(shows)


def _get_show_model(show):
    """There isn't enough info to uniquely identify the show by title and date
    because the TiVo doesn't expose recording time, so just use the TiVo id
    """

    tivo_id = show['tivo_id']

    try:
        return models.Show.objects.get(tivo_id=tivo_id)
    except models.Show.DoesNotExist:
        model = models.Show()
        model.tivo_id = tivo_id
        model.title = show['title']
        model.description = show.get('description', "")
        model.date = show['date']
        model.duration = show['duration']
        model.url = show['link_url']
        model.size = show['size']
        model.save()

    return model


def _match_title(title, s):
    """check if title contains the given substring"""
    if not s:
        return True
    s = s.lower()
    return title.find(s) != -1


def _match_wish(title, wish):
    """check if title matches the wish keywords"""
    if not _match_title(title, wish.keyword1):
        return False
    if not _match_title(title, wish.keyword2):
        return False
    if not _match_title(title, wish.keyword3):
        return False
    return True


def _on_wishlist(shows):
    """check if there's a matching wishlist keyword entry for these shows"""

    wishes = models.WishKeyword.objects.all()
    for wish in wishes:
        logger.info(wish)

    # naive search.  i'm tired and half drunk
    wshows = []

    for show in shows:
        title = show.title.lower()
        logger.debug("Checking show: '%s' against wish list" % title)

        for wish in wishes:
            if _match_wish(title, wish):
                wshows.append(show)
                break

    return wshows


def _update_download_queue(shows):
    """add missing shows to the download queue"""
    # slow, but simple:
    tmp = []
    for show in shows:
        try:
            models.LibraryItem.objects.get(show=show)
            # already on the queue list or previously processed, so skip it.
        except models.LibraryItem.DoesNotExist:
            item = models.LibraryItem()
            item.show = show
            item.save()
            tmp.append(show)
    return tmp


def _update_show_models(job, shows):
    """Create shows and update m2m relationship with jobs"""
    show_models = []

    for show in shows:
        # skip any shows that don't have a tivo_id and valid url
        if show['tivo_id'] == -1:
            logger.debug("No tivo id for show %s.  Skipping." % show['title'])
            continue
        if not show['link_url']:
            logger.debug("No link url for show %s.  Skipping." % show['title'])
            continue

        show_model = _get_show_model(show)

        # tag job model with the new show:
        job.shows.add(show_model)
        show_models.append(show_model)

    return show_models

