import os

import requests
from requests.auth import HTTPDigestAuth

base_url = "https://monstertivo/nowplaying/"
index_url = "index.html"

def tivoget(url=index_url):

    url = base_url + url
    user = "tivo"
    password = os.environ.get('MAK')
    if not password:
        raise RuntimeError("Environment variable MAK not set.")

    auth = HTTPDigestAuth(user, password)
    r = requests.get(url, verify=False, auth=auth)

    if r.status_code != 200:
        raise Exception("Failed to download url %s" % url)
    else:
        return r.text

if __name__=='__main__':
    html = tivoget()
    print html
