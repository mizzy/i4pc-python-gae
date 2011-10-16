import sys
sys.path.append('../lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from basehandler import BaseHandler, h
import os
import simplejson
from models.instagram_wrapper import Instagram
import base
from google.appengine.api import memcache
import datetime
import time
import re
from instagram.bind import InstagramAPIError
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class RelationshipHandler(BaseHandler):
    def get(self, user_id, feed=None):
        instagram = Instagram()
        session = get_current_session()
        instagram.set_access_token(
            access_token = session['access_token']
            )

        user = session['user']
        relationship = instagram.relationship(owner_id=user_id, my_id=user['id'])
        self.response.out.write(simplejson.dumps(relationship))
        
def main():
    app = webapp.WSGIApplication([
        ('/relationship/(.+)', RelationshipHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
