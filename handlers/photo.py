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
import time
from instagram.bind import InstagramAPIError
from google.appengine.api import memcache
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class PhotoHandler(BaseHandler):
    def get(self, media_id):
        if self.request.host == 'instagrampc.appspot.com' or self.request.host == 'www.instagram.jp':
            return self.redirect('http://www.i4pc.jp' + self.request.path, permanent=True )

        instagram = Instagram()
        session = get_current_session()

        if session.has_key('access_token'):
            instagram.set_access_token(
                    access_token = session['access_token']
                    )
            login = True
            user  = session['user']
        else:
            login = False
            user  = None

        try:
            media = instagram.media(media_id)
        except InstagramAPIError, e:
            return base.error(self, 500, e.error_message.capitalize())
        except:
            return base.error(self)
        
        seconds = int(time.time() - time.mktime(media.created_time.timetuple()))
        if seconds < 3600:
            media.time_ago = str(seconds / 60)    + 'm'
        elif seconds < 86400:
            media.time_ago = str(seconds / 3600)  + 'h'
        else:
            media.time_ago = str(seconds / 86400) + 'd'

        try:
            comments = instagram.media_comments(media_id)
        except InstagramAPIError, e:
            return base.error(self, 500, e.error_message.capitalize())
        except:
            return base.error(self)

        try:
            owner = instagram.user(media.user['id'])
        except InstagramAPIError, e:
            return base.error(self, 500, e.error_message.capitalize())
        except:
            return base.error(self)

        try:
            likers = instagram.media_likes(media_id)
        except InstagramAPIError, e:
            return base.error(self, 500, e.error_message.capitalize())
        except:
            return base.error(self)

        if user and hasattr(media, 'user_has_liked') and not media.user_has_liked:
            if memcache.get('user_has_liked_%s_%s' % ( user['id'], media.id ) ):
                media.user_has_liked = True
                media.like_count = media.like_count + 1

        path = base.set_template('photo')
        self.response.out.write(template.render(path, {
            'user'    : user,
            'owner'   : owner,
            'media'   : media,
            'comments': comments,
            'likers'  : likers,
            'login'   : login,
            'path'    : self.request.path,
            }))

def main():
    app = webapp.WSGIApplication([
        ('/photo/(.+)', PhotoHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
