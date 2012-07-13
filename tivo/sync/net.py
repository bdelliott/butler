import logging
import os

import requests
from requests.auth import HTTPDigestAuth

logger = logging.getLogger(__name__)

base_url = "https://monstertivo/nowplaying/"
index_url = "index.html"

def tivoget(url=index_url):

    if not url.startswith("http"):
        # relative url
        url = base_url + url

    user = "tivo"
    password = os.environ.get('MAK')
    if not password:
        raise RuntimeError("Environment variable MAK not set.")

    auth = HTTPDigestAuth(user, password)
    r = requests.get(url, verify=False, auth=auth)

    if r.status_code == 503:
        # tivo is angry - i think this is too many attempted downloads per unit
        # time.  just need to wait a bit and try again.
        tivo_message = r.headers.get('tivo-message', "")
        logger.warn("TiVo 503 error: %s" % tivo_message)
        raise Exception("Grouchy TiVo: %s" % tivo_message)

    if r.status_code == 200:
        logger.debug("Content type: %s" % r.headers['content-type'])
        logger.debug("mime_type: %s" % _mime_type(r))

    if r.status_code != 200:
        raise Exception("Failed to download url %s" % url)

    # either return text or binary depending on the content type
    if _mime_type(r) == "video/x-tivo-mpeg":
        logger.debug("Returning binary content (iter)")
        # return an interator to the binary content:
        return r.iter_content(chunk_size=1024)
    else:
        logger.debug("Returning text content")
        return r.text

def _mime_type(r):
    ctype = r.headers['content-type']

    x = ctype.find(";")
    if x != -1:
        ctype = ctype[0:x]
    return ctype

if __name__=='__main__':
    html = tivoget()
    print html
