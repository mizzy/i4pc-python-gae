import sys
sys.path.append('../lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from basehandler import BaseHandler, h
import os
import simplejson
from instagram import Instagram
import base
import datetime
from datamodel import Feed
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class NewsHandler(BaseHandler):
    def get(self):
        instagram = Instagram()
        result = instagram.get_news()
        path = base.set_template('news')
        session = get_current_session()
        self.response.out.write(template.render(path, {
            'items'     : result['items'][0]['updates'],
            'user'      : instagram.get_user_info(session['ds_user_id']),
            'followings': instagram.get_following(session['ds_user_id'])['users'],
            'login'     : True }))

def main():
    app = webapp.WSGIApplication([
        ('/news', NewsHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
