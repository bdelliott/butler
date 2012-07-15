import logging
import os
import re
import subprocess

from sync import models
from sync import net

logger = logging.getLogger(__name__)

def get_mpeg_info(filename):
    """Get MPEG file metadata of interest"""
    videos_dir = _dir()
    p = subprocess.Popen(["ffmpeg", "-i", filename], cwd=videos_dir,
            stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    rc = p.wait()

    out = p.stdout.read()
    pattern = r'Video: mpeg2video \(Main\), (?P<vdata>.*?)\n'
    m = re.search(pattern, out)

    vdata = m.groups()[0]
    mdata = vdata.split(", ")
    logger.info(mdata)

    resolution = mdata[1].split(" ")[0]
    (width, height) = resolution.split("x")
    width = int(width)
    height = int(height)
    logger.info("%dx%d" % (width, height))

    bitrate = mdata[2].split(" ")[0] # kb/s

    fps = float(mdata[3].split(" ")[0])

    return {
        "width": width,
        "height": height,
        "bitrate": bitrate,  # kb/s
        "fps": fps,
    }

def get_todo_list():
    """Get list of unfinished library items"""

    # assume that a "hinted" file is complete
    return models.LibraryItem.objects.filter(h264=False)

    
def process(item):
    """Process the given item"""

    if not item.downloaded:
        # acquire file!
        _download(item)

    if not item.decoded:
        _decode(item)

    if not item.h264:
        _transcode(item)


def _decode(item):
    """Run tivodecode on the file to turn it into a plain vanilla mpeg"""
    tivo_filename = _filename(item)
    logger.info("Decoding %s" % tivo_filename)

    mpeg_filename = _filename(item, ext="mpg")
    videos_dir = _dir()

    p = subprocess.Popen(["tivodecode", "--mak", os.environ["MAK"], "--out",
        mpeg_filename, tivo_filename], videos_dir)
    rc = p.wait()

    logger.info("tivodecode returned %d" % rc)
    if rc == 0:
        # success!
        item.decoded = True
        item.save()
    else:
        raise Exception("Tivodecode failed on file %s with rc %d" %
                (tivo_filename, rc))


def _dir():
    return "videos"

    
def _download(item):
    """Download the file to local storage.  Tivo lies and claims it's going to
    do chunked encoding, but it's bullshit.  It just serves the whole file in 1 
    shot.
    """

    filename = _filename(item)
    filename = os.path.join(_dir(), filename)
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
    return fname


def _scaled_resolution(width, height):
    """Scale resolution down"""
    if width > 1000:
        width /= 2
        height /= 2

    res = "%dx%d" % (width, height)
    logger.info("Scaled resolution: %s" % res)
    return res


def _transcode(item):
    mpeg_filename = _filename(item, ext="mpg")
    mp4_filename = _filename(item, ext="mp4")

    vdata = get_mpeg_info(mpeg_filename)
    logger.info(vdata)

    res = _scaled_resolution(vdata['width'], vdata['height'])

    videos_dir = _dir()
    p = subprocess.Popen(["ffmpeg", "-i", mpeg_filename, "-s", res,
                          "-sameq", mp4_filename], cwd=videos_dir)
    rc = p.wait()
    #ffmpeg -i input -res 1/2 or 1/4 -sameq out

    logger.debug("ffmpeg returned %d" % (rc))

    item.h264 = True
    item.save()
