from django.db import models

class SyncJob(models.Model):
    """Represent one sync/extraction run"""
    start = models.DateTimeField("Job start time", auto_now_add=True)
    end = models.DateTimeField("Job end time", null=True, blank=True)

    def __str__(self):
        return "[Start: %s, End: %s]" % (self.start, self.end)

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

    jobs = models.ManyToManyField(SyncJob)

class WishKeyword(models.Model):
    """Search keyword(s) to match in an AND fashion"""
    keyword1 = models.CharField("Keyword 1", max_length=80)
    keyword2 = models.CharField("Keyword 2", max_length=80, default="")
    keyword3 = models.CharField("Keyword 3", max_length=80, default="")
