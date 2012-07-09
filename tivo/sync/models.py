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
    date = models.DateTimeField("Date/time of recording")
    duration = models.IntegerField("Duration in minutes")
    url = models.URLField("MPEG PS File URL", max_length=1024)
    size = models.IntegerField("File size in MB")

    jobs = models.ManyToManyField(SyncJob)
