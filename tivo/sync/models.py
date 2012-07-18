import os

from django.db import models

class Show(models.Model):
    """A single show from the Tivo."""
    tivo_id = models.IntegerField("Show id as exposed by Tivo links")
    title = models.CharField("Title", max_length=128)
    description = models.CharField("Description", max_length=512, default="",
            blank=True)
    date = models.DateField("Date of recording")
    duration = models.IntegerField("Duration in minutes")

    # some dbag shows can't be downloaded from TiVo:
    url = models.URLField("MPEG PS File URL", max_length=1024, null=True,
            blank=True)
    size = models.IntegerField("File size in MB")

    def datestr(self):
        """YYYYMMDD"""
        return self.date.strftime("%Y%m%d")

    def __str__(self):
        return "[%s - %d - %s]" % (self.date, self.tivo_id, self.title)


class SyncJob(models.Model):
    """Represent one sync/extraction run"""
    start = models.DateTimeField("Job start time", auto_now_add=True)
    end = models.DateTimeField("Job end time", null=True, blank=True)

    shows = models.ManyToManyField(Show)

    def __str__(self):
        return "[Start: %s, End: %s]" % (self.start, self.end)


class LibraryItem(models.Model):
    """An item to download, re-encode, and add stream hints to"""
    show = models.ForeignKey(Show)

    downloaded = models.BooleanField(default=False)
    decoded = models.BooleanField(default=False)
    h264 = models.BooleanField(default=False)

    def filename(self, ext="tivo"):
        title = self.show.title
        # ffmpeg can't handle a filename with a ':' character
        title = title.replace(":", "_")
        fname = "%s.%s.%d.%s" % (self.show.datestr(), title,
                self.show.tivo_id, ext)
        return fname

    def url(self):
        return "/videos/%s" % (self.filename(ext="mp4"))

    def vdir(self):
        d = "/Users/bde/dev/butler/tivo/videos"
        return d

    def __str__(self):
        return "[%s: downloaded=%d, decoded=%d, h264=%d]" % (self.show,
                self.downloaded, self.decoded, self.h264)

class WishKeyword(models.Model):
    """Search keyword(s) to match in an AND fashion"""
    keyword1 = models.CharField("Keyword 1", max_length=80)
    keyword2 = models.CharField("Keyword 2", max_length=80, default="",
            blank=True)
    keyword3 = models.CharField("Keyword 3", max_length=80, default="",
            blank=True)

    def __str__(self):
        return "['%s', '%s', '%s']" % (self.keyword1, self.keyword2,
                self.keyword3)
