import sys
sys.path.append('../lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

from basehandler import BaseHandler, h
import os
import base
import datetime
from models.instagram_wrapper import Instagram

class FeedHandler(BaseHandler):
    def get(self):
        session   = get_current_session()
        instagram = Instagram()

        if session.has_key('access_token'):
            instagram.set_access_token(
                    access_token = session['access_token']
                    )
            feed, pagination = instagram.user_media_feed(
                count   = 200,
                user_id = session['user']['id'],
                max_id  = None,
                )
            title = 'Feed - I4PC'
        else:
            feed = instagram.media_popular(count=200, max_id=None)
            title = 'Popular - I4PC'
            
        path = base.set_template('feed')
        self.response.out.write(template.render(path, {
            'feed' : feed,
            'title': title,
            }))

def main():
    app = webapp.WSGIApplication([
        ('/feed', FeedHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
