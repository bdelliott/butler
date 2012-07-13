import logging
import os
import subprocess

from sync import models
from sync import net

logger = logging.getLogger(__name__)

def get_todo_list():
    """Get list of unfinished library items"""

    # assume that a "hinted" file is complete
    return models.LibraryItem.objects.filter(hinted=False)
    
def process(item):
    """Process the given item"""

    if not item.downloaded:
        # acquire file!
        _download(item)

    if not item.decoded:
        _decode(item)

def _decode(item):
    """Run tivodecode on the file to turn it into a plain vanilla mpeg"""
    tivo_filename = _filename(item)
    logger.info("Decoding %s" % tivo_filename)

    mpeg_filename = _filename(item, ext="mpg")
    p = subprocess.Popen(["tivodecode", "--mak", os.environ["MAK"], "--out",
        mpeg_filename, tivo_filename])
    rc = p.wait()

    logger.info("tivodecode returned %d" % rc)
    if rc == 0:
        # success!
        item.decoded = True
        item.save()
    else:
        raise Exception("Tivodecode failed on file %s with rc %d" %
                (tivo_filename, rc))


    
def _download(item):
    """Download the file to local storage.  Tivo lies and claims it's going to
    do chunked encoding, but it's bullshit.  It just serves the whole file in 1 
    shot.
    """

    filename = _filename(item)
    logger.info("Downloading '%s' to %s" % (item.show, filename))

    f = open(filename, "wb")

    buf = net.tivoget(item.show.url)
    for chunk in buf:
        f.write(chunk)

    f.close()

    item.downloaded = True
    item.save()
    

def _filename(item, ext="tivo"):
    if not os.path.exists("videos"):
        os.mkdir("videos")

    fname = item.show.title + "." + ext
    path = os.path.join("videos", fname)
    return path
