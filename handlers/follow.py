import sys
sys.path.append('../lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from basehandler import BaseHandler, h
import os
import simplejson
from models.instagram_wrapper import Instagram
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class FollowHandler(BaseHandler):
    def get(self, owner_id):
        instagram = Instagram()
        session = get_current_session()
        instagram.set_access_token(
            access_token = session['access_token']
            )
        res = instagram.follow_user(owner_id=owner_id, my_id=session['user']['id'])
        self.response.out.write(simplejson.dumps(res[0]))

class UnfollowHandler(BaseHandler):
    def get(self, owner_id):
        instagram = Instagram()
        session = get_current_session()
        instagram.set_access_token(
            access_token = session['access_token']
            )
        res = instagram.unfollow_user(owner_id=owner_id, my_id=session['user']['id'])
        self.response.out.write(simplejson.dumps(res[0]))

            
def main():
    app = webapp.WSGIApplication([
        ('/follow/(.+)',   FollowHandler),
        ('/unfollow/(.+)', UnfollowHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
