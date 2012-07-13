import datetime
import logging
import os

import bs4

logger = logging.getLogger(__name__)

def read_folder(html):
    e = Extractor(html)
    return e.extract()

def read_index(html):
    e = Extractor(html)
    return e.extract()

class ExtractionException(Exception):
    pass

class Extractor(object):
    def __init__(self, html):
        self.soup = bs4.BeautifulSoup(html, from_encoding="utf-8")
        self.shows = None

    def extract(self):
        trs = self.soup.find_all(self._tr_matcher)
        items = [self._extract_show_or_folder(tr) for tr in trs]
        return items

    def _extract_show_or_folder(self, t):
        """Starting with a tr tag, extract block of content pertaining to a
        single show or folder

        *Warning: Yucky HTML data extraction follows.
        """
        logger.debug("Show/folder extraction:")

        # first col is an img:
        t = t.img
        is_folder = self._is_folder(t)
       
        # second col is a channel logo, many entries do not have this:
        td = t.find_next("td")
        if td.img:
            # Yep, this has a channel logo.  Skip!
            logger.debug("skipping channel logo")
            td = td.find_next("td")

        # third col is a title and an optional description
        if not td.has_key("valign"):
            # some 'title' blocks have an outer td with no attribs
            td = td.td
            assert(td.has_key("valign"))

        title = td.b.text.strip()
        logger.debug("Title: %s" % title)

        # 2 special folders:
        if title == "HD Recordings":
            is_folder = True
        if title == "TiVo Suggestions":
            is_folder = True

        # wrong crazy matching...
        br = td.b.find_next_sibling("br")
        if br:
            description = br.text.strip()
        else:
            description = ""
        logger.debug("Description: %s" % description)
        
        # fourth col is a date: (e.g. Sat 7/5)
        td_date = td.find_next("td")
        if not td_date.text:
            # no date for this show/folder
            day_of_week = None
            date = None
        else:
            # yes there is a date to parse
            # it's day of week e.g. Sat
            # some whitespace and a date like 7/7
            txt = td_date.text.strip()
            txt = txt.replace(" ", "")
            day_of_week = txt[0:3]
            date = txt[3:6]
            (month, day) = date.split("/")
            month = int(month)
            day = int(day)
            year = datetime.date.today().year
            date = datetime.datetime(year, month, day)
        logger.debug("Day of week: %s" % day_of_week)
        logger.debug("Date: %s" % date)

        # fifth column is 'Size'.  the content is either
        # a number of items in the folder of a runtime and
        # file size (which may or may not be right?)
        td_size = td_date.find_next_sibling("td")
        assert(td_size.has_key("align"))

        num_items = None
        mins = None
        sz = None

        if is_folder:
            # 1 line: 3 items
            num_items = td_size.text.strip().split(" ")[0]
            logger.debug("Number of folder items: %s" % num_items)
        else:
            # runtime/filesize:
            # 2 lines: 0:30:00
            #          990 MB
            runtime = td_size.contents[0]
            logger.debug("Runtime: %s" % runtime)
            (hours, mins, secs) = runtime.split(":")
            hours = int(hours)
            mins = int(mins)
            mins += hours * 60
            logger.debug("Runtime in minutes: %d" % mins)

            (sz, units) = td_size.br.text.strip().split()

            # convert runtime to minutes:

            sz = float(sz)
            if units == "GB":
                sz = sz * 1024  # convert to MB
            logger.debug("File size: %0.2f MB" % sz)
            
        # sixth and final column are 'Links'.  Either link to the
        # download or link to the folder content page:
        td_links = td_size.find_next_sibling("td")
        assert(td_links.has_key("align"))

        # this should get either the folder url or the MPEG PS download link:
        if not td_links.a:
            link_url = None
        else:
            link_url = td_links.a['href']

        logger.debug("Link URL: %s" % link_url)

        return {
            "is_folder": is_folder,
            "title": title,
            "description": description,
            "day_of_week": day_of_week,
            "date": date,
            "num_items": num_items,
            "duration": mins,
            "size": sz,
            "link_url": link_url,
        }

    def _is_folder(self, img):
        """Next we should find a td with an image inside of it either with a
        channel logo, expired img, or a folder icon.
        """
        src = img['src']
        return src.endswith("folder.png")

    def _pkids(self, tag):
        """debug method to print kids"""
        for k in tag.children:
            print "'%s'" % k
            print "-"*80


    def _tr_matcher(self, tag):
        bgcolor = tag.get('bgcolor')
        if not bgcolor:
            return False

        return bgcolor in ['F5F595', 'F5F5B5']


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)

    """
    test_dir = os.path.join(os.getcwd(), "test")
    test_file = open(os.path.join(test_dir, "index.html"))
    html = test_file.read()
    test_file.close()

    # extract show content from the HTML mess
    items = read_index(html)
    for item in items:
        print item

    # extract a folder
    folder_items = [i for i in items if i["is_folder"]]
    item = folder_items[0]

    url = item["link_url"]
    import net
    html = net.tivoget(url)
    print html
    soup = bs4.BeautifulSoup(html, from_encoding="utf-8")
    print soup.prettify()
    """

    test_dir = os.path.join(os.getcwd(), "testhtml")
    test_file = open(os.path.join(test_dir, "folder.html"))
    html = test_file.read()
    test_file.close()

    items = read_folder(html)
    for item in items:
        for k,v in item.iteritems():
            print "%s = %s" % (k,v)
        print "-"*80
