from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import appengine_utilities.sessions
from basehandler import BaseHandler, h
import os
import urllib
import Cookie
import time
import simplejson
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch


class IndexHandler(BaseHandler):
    def get(self, *args):
        session = appengine_utilities.sessions.Session()
        if not session.has_key('sessionid'):
            self.redirect('/login')
            return
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')

        res = urlfetch.fetch(
            url='http://instagr.am/api/v1/feed/timeline/?',
            headers={
                'Cookie': 'ds_user=%s; ds_user_id=%s; sessionid=%s'
                % ( session['ds_user'], session['ds_user_id'], session['sessionid'])  
                },
            method='GET')

        items = simplejson.loads(res.content)['items']
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, { 'items': items }))
        #self.response.out.write(items[0]['image_versions'][1]['url'])

class LoginHandler(BaseHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'login.html')
        self.response.out.write(template.render(path, { 'status': self.request.get('status') }))

    def post(self):
        cookie = Cookie.SimpleCookie()

        res = urlfetch.fetch('http://instagr.am/api/v1/accounts/login/',
                             payload=urllib.urlencode({
                                 'username':  self.request.get('username'),
                                 'password':  self.request.get('password'),
                                 'device_id': 'hoge',
                             }),
                             method='POST',
                             deadline=10)

        result = simplejson.loads(res.content)
        if result['status'] == 'fail':
            self.redirect('/login?status=login%20error')
            return
        
        cookie.load(res.headers['Set-Cookie'])

        session = appengine_utilities.sessions.Session()
        session['sessionid']  = cookie['sessionid'].value
        session['ds_user']    = cookie['ds_user'].value
        session['ds_user_id'] = cookie['ds_user_id'].value
        
        self.redirect('/')

        
routing = [
#    ('/user/(.+)', UserHandler),
    ('/login', LoginHandler),
    ('/', IndexHandler),
    ]
    
application = webapp.WSGIApplication(
    routing,
    debug=True
)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

