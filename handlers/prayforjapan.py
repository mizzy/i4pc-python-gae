import sys
sys.path.append('../lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from basehandler import BaseHandler, h
import os
import simplejson
from datamodel import Feed
import base
from models.instagram_wrapper import Instagram
import re
from google.appengine.api import memcache
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class PrayForJapanHandler(BaseHandler):
    def get(self, *args):
        session     = get_current_session()
        instagram   = Instagram()
        max_id      = self.request.get('max_id')
        prev_max_id = max_id

        if session.has_key('access_token'):
            instagram.set_access_token(
                    access_token = session['access_token']
                    )
            login = True
            user  = session['user']
        else:
            login = False
            user  = None

        path             = base.set_template('prayforjapan')
        feed, pagination = instagram.tag_recent_media(tag_name='prayforjapan', count=50, max_id=max_id)

        title   = '#prayforjapan'
        body_id = 'popular'

        max_id = None
        if pagination.has_key('next_max_id'):
            max_id = pagination['next_max_id']

        if user:
            for media in feed:
                if memcache.get('user_has_liked_%s_%s' % ( user['id'], media.id ) ):
                    media.user_has_liked = True
                    media.like_count = media.like_count + 1

        self.response.out.write(template.render(path, {
            'feed'       : feed,
            'user'       : user,
            'login'      : login,
            'max_id'     : max_id,
            'title'      : title,
            'body_id'    : feed,
            'path'       : self.request.path,
            'prev_max_id': prev_max_id,
            }))

def main():
    app = webapp.WSGIApplication([
        ('/prayforjapan', PrayForJapanHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
