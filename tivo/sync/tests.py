"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase

import sync
from . import models
from . import queue
from . import views

class SyncTestCase(TestCase):

    def _create_show(self):
        show = {
            "title": "The Walking Dead",
            "date": datetime.datetime.now(),
            "link_url": "http://foo.com/blah.mpg",
            "duration": 60,
            "size": 900,
        }
        return show
 
    def test_sync_in_progress(self):
        self.assertFalse(sync.sync_in_progress())

        job = models.SyncJob()
        job.save()

        self.assertTrue(sync.sync_in_progress())

        now = datetime.datetime.now()
        job.end = now
        job.save()

        self.assertFalse(sync.sync_in_progress())

    def test_show_model(self):
        show = self._create_show()
        show_model = queue._get_show_model(show)
        show_id = show_model.id

        # calling it again should return the same row
        show_model = queue._get_show_model(show)
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

        shows = queue._update_show_models(job, shows)
        self.assertEqual(1, len(shows))
        show = models.Show.objects.all()[0]
        num_shows = len(job.shows.all())
        self.assertEqual(1, num_shows)
