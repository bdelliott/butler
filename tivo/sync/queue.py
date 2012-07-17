import fcntl
import logging
import os
import re
import select
import subprocess
import time

from sync import models
from sync import net

logger = logging.getLogger(__name__)

FFMPEG = "/usr/local/bin/ffmpeg"

def get_mpeg_info(videos_dir, filename):
    """Get MPEG file metadata of interest"""
    logger.info("Getting info from %s/%s" % (videos_dir, filename))
    if not os.path.exists(videos_dir):
        raise Exception("%s dir does not exist!" % videos_dir)
    path = os.path.join(videos_dir, filename)
    if not os.path.exists(path):
        raise Exception("%s does not exist!" % path)

    p = subprocess.Popen([FFMPEG, "-i", filename], cwd=videos_dir,
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

    # assume that a "h264" encoded file is complete
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
    tivo_filename = item.filename()
    logger.info("Decoding %s" % tivo_filename)

    mpeg_filename = item.filename(ext="mpg")
    videos_dir = item.vdir()

    p = subprocess.Popen(["/usr/local/bin/tivodecode", "--mak", os.environ["MAK"], 
        "--out", mpeg_filename, tivo_filename], cwd=videos_dir,
        stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    rc = p.wait()

    logger.info("tivodecode returned %d" % rc)
    logger.info("tivodecode output: '%s'" % p.stdout.read())
    if rc == 0:
        # success!
        item.decoded = True
        item.save()
    else:
        raise Exception("Tivodecode failed on file '%s' with rc %d" %
                (tivo_filename, rc))

    
def _download(item):
    """Download the file to local storage.  Tivo lies and claims it's going to
    do chunked encoding, but it's bullshit.  It just serves the whole file in 1 
    shot.
    """

    filename = item.filename()
    filename = os.path.join(item.vdir(), filename)
    logger.info("Downloading '%s' to %s" % (item.show, filename))

    f = open(filename, "wb")

    buf = net.tivoget(item.show.url)
    for chunk in buf:
        f.write(chunk)

    f.close()

    item.downloaded = True
    item.save()
    

def _scaled_resolution(width, height):
    """Scale resolution down"""
    if width > 1000:
        width /= 2
        height /= 2

    res = "%dx%d" % (width, height)
    logger.info("Scaled resolution: %s" % res)
    return res


def _transcode(item):
    mpeg_filename = item.filename(ext="mpg")
    mp4_filename = item.filename(ext="mp4")
    videos_dir = item.vdir()

    vdata = get_mpeg_info(videos_dir, mpeg_filename)
    logger.info(vdata)

    res = _scaled_resolution(vdata['width'], vdata['height'])

    ffmpeg_args = _transcode_ffmpeg_args(mpeg_filename, mp4_filename, res)
    rc = _transcode_ffmpeg_subprocess(ffmpeg_args, videos_dir)

    item.h264 = True
    item.save()

def _transcode_ffmpeg_args(mpeg_filename, mp4_filename, res):
    """Generate list of iPad compatible h.264 video options"""

    """
    697  ffmpeg -i Chef\ Wanted\ With\ Anne\ Burrell\:\ \"The\ Re-Launch\".mpg
    -strict experimental -acodec aac -ac 2 -ab 160k -s 960x540 -vcodec libx264
    -vpre iPod640 -b 1200k -f mp4 -threads 0 chef.conversionmatrixsettings.mp4
    """
    return [FFMPEG, "-i", mpeg_filename, "-strict", "experimental",
            "-acodec", "aac", "-ac", "2", "-ab", "160k", "-s", res,
            "-vcodec", "libx264", "-vpre", "iPod640", "-b", "1200k",
            "-f", "mp4", "-threads", "0", mp4_filename]


def _transcode_ffmpeg_subprocess(ffmpeg_args, videos_dir):
    p = None
    try:
        p = subprocess.Popen(ffmpeg_args, cwd=videos_dir, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        
        #p = subprocess.Popen(["ffmpeg", "-i", mpeg_filename, "-s", res,
        #                      "-sameq", mp4_filename], cwd=videos_dir)
        fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL,
                fcntl.fcntl(p.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,)

        while p.returncode is None:
            readx = select.select([p.stdout.fileno()], [], [])[0]
            if readx:
                out = p.stdout.read()
                out = out.replace("\r", "\n")
                logger.debug(out.strip())
            time.sleep(0.1)

        if rc != 0:
            logger.debug("ffmpeg returned %d" % (rc))
            raise Exception("ffmpeg failure")
    except:
        logger.exception("FFMPEG subprocess exception")
        raise Exception("FFMPEG/subprocess failure")
        p.kill()    

