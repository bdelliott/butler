"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime
import logging

from django.test import TestCase

import sync
from . import models
from . import showfilter
from . import views

logger = logging.getLogger(__name__)

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
    
    def _create_show_model(self, **kwargs):
        values = {
            "title": "Late Night With Jimmy Fallon",
            "description": "",
            "date": datetime.datetime.now(),
            "duration": 10,
            "url": "http://www.foo.com",
            "size": 1024,
        }
        values.update(kwargs)
        
        show = models.Show(**values)
        show.save()
        return show

    def _create_wish_model(self, **kwargs):
        wish = models.WishKeyword(**kwargs)
        wish.save()
        return wish
 
    def test_sync_in_progress(self):
        self.assertFalse(sync.latest_job())

        job = models.SyncJob()
        job.save()

        self.assertFalse(sync.latest_job().end)

        now = datetime.datetime.now()
        job.end = now
        job.save()

        self.assertTrue(sync.latest_job().end)

    def test_show_model(self):
        show = self._create_show()
        show_model = showfilter._get_show_model(show)
        show_id = show_model.id

        # calling it again should return the same row
        show_model = showfilter._get_show_model(show)
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

        shows = showfilter._update_show_models(job, shows)
        self.assertEqual(1, len(shows))
        show = models.Show.objects.all()[0]
        num_shows = len(job.shows.all())
        self.assertEqual(1, num_shows)

    def test_wishlist(self):
        ninja_title = "American Ninja Warrior"
        shows = [
            self._create_show_model(title="Late Night With Jimmy Fallon"),
            self._create_show_model(title=ninja_title),
        ]

        wshows = showfilter._on_wishlist(shows)
        self.assertEqual(0, len(wshows))

        wish = self._create_wish_model(keyword1="ninja")

        wshows = showfilter._on_wishlist(shows)
        self.assertEqual(1, len(wshows))
        self.assertEqual(ninja_title, wshows[0].title)

        wish2= self._create_wish_model(keyword1="late", keyword2="with",
                keyword3="fallon")
        wshows = showfilter._on_wishlist(shows)
        self.assertEqual(2, len(wshows))


