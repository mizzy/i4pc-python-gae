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
from instagram.bind import InstagramAPIError
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class IndexHandler(BaseHandler):
    def get(self, *args):
        if self.request.host == 'instagrampc.appspot.com' or self.request.host == 'www.instagram.jp':
            return self.redirect('http://www.i4pc.jp/', permanent=True)

        session = get_current_session()
        instagram   = Instagram()
        max_id      = self.request.get('max_id')
        prev_max_id = max_id

        first_page = True
        if max_id:
            first_page = False
            
        if session.has_key('access_token'):
            instagram.set_access_token(
                    access_token = session['access_token']
                    )
            login = True
            user  = session['user']
        else:
            login = False
            user  = None

        if self.request.path == '/popular' or login == False:
            path    = base.set_template('popular')

            try:
                feed = instagram.media_popular(count=50, max_id=max_id)
            except InstagramAPIError, e:
                return base.error(self, 500, e.error_message.capitalize())
            except:
                return base.error(self)

            title   = 'Popular'
            body_id = 'popular'
        else:
            path             = base.set_template('index')
            if self.request.path == '/liked':
                try:
                    feed, pagination = instagram.user_liked_feed(
                        count   = 20,
                        max_id  = max_id,
                        user_id = user['id'],
                        )
                    title   = 'Liked'
                    body_id = 'liked'
                    max_id  = None
                except InstagramAPIError, e:
                    return base.error(self, 500, e.error_message.capitalize())
                except:
                    return base.error(self)
            else:
                try:
                    feed, pagination = instagram.user_media_feed(
                        count   = 20,
                        max_id  = max_id,
                        user_id = user['id'],
                        )
                    title   = 'Feed'
                    body_id = 'feed'
                    max_id  = None
                except InstagramAPIError, e:
                    return base.error(self, 500, e.error_message.capitalize())
                except:
                    return base.error(self)
                
            if pagination.has_key('next_max_id'):
                max_id = pagination['next_max_id']
            elif pagination.has_key('next_max_like_id'):
                max_id = pagination['next_max_like_id']
                

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
            'first_page' : first_page,
            }))

def main():
    app = webapp.WSGIApplication([
        ('/.*', IndexHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
