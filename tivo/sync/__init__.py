import logging

from . import extractor
from . import net

logger = logging.getLogger(__name__)

def get_shows():
    index_html = net.tivoget()
    items = extractor.read_index(index_html)
    shows = []

    skip_folders = ['tivo suggestions', 'hd recordings']
    for item in items:
        if item['is_folder']:
            if item['title'].lower() not in skip_folders:
                logger.info("Reading folder: %s" % item['title'])
                url = item['link_url']
                folder_html = net.tivoget(url)
                folder_items = extractor.read_folder(folder_html)
                shows.extend(folder_items)
        else:
            shows.append(item)


    logger.info("%d shows extracted" % len(shows))
    return shows
    
