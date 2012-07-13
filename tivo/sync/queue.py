import logging

from sync import models

logger = logging.getLogger(__name__)

def update(job, shows):
    # update m2m relationships
    shows = _update_show_models(job, shows)  # gets list of Show models.

    # prune to things on the "wish list"
    shows = _on_wishlist(shows)

    return _update_download_queue(shows)


def _get_show_model(show):
    # sanity check some data:

    try:
        return models.Show.objects.get(title=show['title'], date=show['date'],
                url=show['link_url'])
    except models.Show.DoesNotExist:
        model = models.Show()
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

    wishes = models.WishKeyword.objects.all()

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


def _update_download_queue(shows):
    """add missing shows to the download queue"""
    # slow, but simple:
    tmp = []
    for show in shows:
        try:
            models.LibraryItem.objects.get(show=show)
            # already on the # queue list, do # nothing.
        except models.LibraryItem.DoesNotExist:
            item = LibraryItem()
            item.show = show
            item.save()
            tmp.append(show)
    return tmp


def _update_show_models(job, shows):
    """Create shows and update m2m relationship with jobs"""
    show_models = []

    for show in shows:
        show_model = _get_show_model(show)

        # tag job model with the new show:
        job.shows.add(show_model)
        show_models.append(show_model)

        return show_models
