"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.utils.timezone import utc



import sync
from . import models
from . import views

class SyncTestCase(TestCase):

    def _create_show(self):
        show = {
            "title": "The Walking Dead",
            "date": datetime.datetime.utcnow().replace(tzinfo=utc),
            "link_url": "http://foo.com/blah.mpg",
            "duration": 60,
            "size": 900,
        }
        return show
 
    def test_sync_in_progress(self):
        self.assertFalse(views._sync_in_progress())

        job = models.SyncJob()
        job.save()

        self.assertTrue(views._sync_in_progress())

        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        job.end = now
        job.save()

        self.assertFalse(views._sync_in_progress())

    def test_show_model(self):
        show = self._create_show()
        show_model = views._get_show_model(show)
        show_id = show_model.id

        # calling it again should return the same row
        show_model = views._get_show_model(show)
        self.assertEqual(show_id, show_model.id)


    def test_get_shows(self):
        """Just make sure we can get some shows.  Yes, this is a crappy
        functional shows.
        """
        shows = sync.get_shows()
        num_shows = len(shows)
        self.assertGreaterEqual(num_shows, 1)

        show = shows[0]
        self.assertTrue(show.has_key("date"))

    def test_update_show_models(self):
        shows = [self._create_show()]
        job = models.SyncJob()
        job.save()

        shows = views._update_show_models(job, shows)
        self.assertEqual(1, len(shows))
        show = models.Show.objects.all()[0]
        num_jobs = len(show.jobs.all())
        self.assertEqual(1, num_jobs)
