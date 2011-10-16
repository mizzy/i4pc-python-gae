import sys
sys.path.append('../lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from basehandler import BaseHandler, h
import os
import base

class DefaultHandler(BaseHandler):
    def get(self, *args):
        path = base.set_template(args[0])
        try:
            self.response.out.write(template.render(path, {}))
        except:
            self.response.set_status(404)
            path = base.set_template('not_found')
            self.response.out.write(template.render(path, {}))

def main():
    application = webapp.WSGIApplication([
        ('/(.+)', DefaultHandler),
        ],
        debug=False)
    run_wsgi_app(application)

if __name__ == "__main__":
  main()
