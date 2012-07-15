from django.db import models

class Show(models.Model):
    """A single show from the Tivo."""
    title = models.CharField("Title", max_length=128)
    description = models.CharField("Description", max_length=512, default="",
            blank=True)
    date = models.DateField("Date of recording")
    duration = models.IntegerField("Duration in minutes")

    # some dbag shows can't be downloaded from TiVo:
    url = models.URLField("MPEG PS File URL", max_length=1024, null=True,
            blank=True)
    size = models.IntegerField("File size in MB")

    def __str__(self):
        return "%s - %s" % (self.date, self.title)

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
