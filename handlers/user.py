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

class UserHandler(BaseHandler):
    def get(self, user_id, feed=None):
        if self.request.host == 'instagrampc.appspot.com' or self.request.host == 'www.instagram.jp':
            return self.redirect('http://www.i4pc.jp' + self.request.path, permanent=True )

        instagram = Instagram()
        session = get_current_session()

        if not session.has_key('access_token'):
            session['redirect_to'] = self.request.path
            return self.redirect('/login')
        else:
            access_token = session['access_token']
            user         = session['user']
            login        = True
            
        instagram.set_access_token(
            access_token = access_token
            )

        try:
            user_searched = instagram.user_find_by_username(user_id)
        except InstagramAPIError, e:
            return base.error(self, 500, e.error_message.capitalize())
        except:
            return base.error(self)
            
        found = None
        if user_searched:
            user_id = user_searched['id']
            found = True

        max_id = self.request.get('max_id')
        prev_max_id = max_id

        if not found and re.match(r'^\d+$', user_id):
            try:
                user_found = instagram.user(user_id)
            except InstagramAPIError, e:
                return base.error(self, 500, e.error_message.capitalize())
            except:
                return base.error(self)

            if user_found:
                url = '/user/%s' % user_found['username']
                if max_id:
                    url = url + '?max_id=%s' % max_id
                return self.redirect(url, permanent=True)

        if feed == 'feed':
            path = base.set_template('user_feed')
            self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        else:
            path = base.set_template('user')

        try:
            feed, pagination = instagram.user_recent_media(
                user_id = user_id,
                max_id  = max_id,
                )
        except InstagramAPIError, e:
            feed       = []
            pagination = {}

        if pagination.has_key('next_max_id'):
            max_id = pagination['next_max_id']
        else:
            max_id = ''

        for media in feed:
            media.pub_date = base.format_date(media.created_time)
            seconds = int(time.time() - time.mktime(media.created_time.timetuple()))
            if seconds < 3600:
                media.time_ago = str(seconds / 60)    + 'm'
            elif seconds < 86400:
                media.time_ago = str(seconds / 3600)  + 'h'
            else:
                media.time_ago = str(seconds / 86400) + 'd'

        try:
            followings, pagination = instagram.user_follows(
                count   = 2000,
                user_id = user_id,
                cursor  = None
                )
        except InstagramAPIError, e:
            followings = []

        private = False
        try:
            owner = instagram.user(user_id)
        except InstagramAPIError, e:
            owner = user_searched
            if e.error_message == 'you cannot view this resource':
                private = True

        for media in feed:
            if memcache.get('user_has_liked_%s_%s' % ( user['id'], media.id ) ):
                media.user_has_liked = True
                media.like_count = media.like_count + 1
        
        try:
            relationship = instagram.relationship(owner_id=user_id, my_id=user['id'])
        except InstagramAPIError, e:
            pass
            
        self.response.out.write(template.render(path, {
            'user'        : user,
            'followings'  : followings,
            'owner'       : owner,
            'feed'        : feed,
            'max_id'      : max_id,
            'prev_max_id' : prev_max_id,
            'login'       : login,
            'mode'        : 'user',
            'path'        : self.request.path,
            'relationship': relationship,
            'private'     : private,
            }))

class FollowingHandler(BaseHandler):
    def get(self, username):
        instagram = Instagram()
        session = get_current_session()

        if not session.has_key('access_token'):
            session['redirect_to'] = self.request.path
            return self.redirect('/login')
        else:
            access_token = session['access_token']
            user         = session['user']

        instagram.set_access_token(
            access_token = session['access_token']
            )
        cursor = self.request.get('cursor')

        user = instagram.user_find_by_username(username)
        follows, pagination = instagram.user_follows(user_id=user['id'], count=20, cursor=cursor)

        next_cursor = None
        if pagination.has_key('next_cursor'):
            next_cursor = pagination['next_cursor']
            
        path = base.set_template('follows')
        self.response.out.write(template.render(path, {
            'follows'     : follows,
            'next_cursor' : next_cursor,
            'user'        : session['user'],
            'owner'       : user,
            'login'       : True,
            'path'        : self.request.path,
            'following'   : True,
            }))

class FollowersHandler(BaseHandler):
    def get(self, username):
        instagram = Instagram()
        session = get_current_session()

        if not session.has_key('access_token'):
            session['redirect_to'] = self.request.path
            return self.redirect('/login')
        else:
            access_token = session['access_token']
            user         = session['user']

        instagram.set_access_token(
            access_token = session['access_token']
            )
        cursor = self.request.get('cursor')

        user = instagram.user_find_by_username(username)
        follows, pagination = instagram.user_followed_by(user_id=user['id'], count=20, cursor=cursor)

        next_cursor = None
        if pagination.has_key('next_cursor'):
            next_cursor = pagination['next_cursor']
            
        path = base.set_template('follows')
        self.response.out.write(template.render(path, {
            'follows'     : follows,
            'next_cursor' : next_cursor,
            'user'        : session['user'],
            'owner'       : user,
            'login'       : True,
            'path'        : self.request.path,
            'following'   : False,
            }))


def main():
    app = webapp.WSGIApplication([
        ('/user/(.+)/following', FollowingHandler),
        ('/user/(.+)/followers', FollowersHandler),
        ('/user/(.+)/(.+)',    UserHandler),
        ('/user/(.+)',         UserHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
