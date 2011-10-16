import sys
sys.path.append('../lib')
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from basehandler import BaseHandler, h
from google.appengine.ext import webapp
import os
from models.instagram_wrapper import Instagram
from gaesessions import SessionMiddleware
from gaesessions import get_current_session
from google.appengine.ext.appstats import recording

class AuthHandler(BaseHandler):
    def get(self):
        instagram = Instagram()
        access_token = instagram.api.exchange_code_for_access_token(
            self.request.get('code')
            )

        instagram.set_access_token(access_token)
        user = instagram.api.user()

        enabled_users = [
            'mizzy', 'nakajijapan', 'demiflare168', 'chcltn', 'usagi_mogmog',
            'glover', 'xx21013271xx', 'micoshiva', 'fujimuu', 'gionby',
            'daiskip', 'higuchama', 'umazura', 'mamarico', 'norizoo',
            'crosside', 'pplog', 'yano3', 'hamaman', 'daigo', 'okuzuran',
            'harunaharuko', 'tnmt', 'nicokuki', 'maruyanma', 'ashlaman',
            'kawashimajunko', 'pinko', 'isodine', 'diyafi', 'kulop', 'atani',
            'sorahoderi', 'chigie', 'milco', 'toykyojapan', 'nakedrocks',
            'uxul', 'miyafuyo', 'taketin', 'ayairo', 'papilio17',
            'mohariyoshi', 'sen', 'mountain_sgmt', 'sugar_sgmt', 'teroma2',
            'bajitette', 'glitter', '8823', 'sandalcc', 'sippo', 'rl_rl_rl',
            'altmk', 'mohemohemo', 'simple_life', 'ayap', 'meganejunkie',
            'koysd', 'ataka', 'tichise', 'kai_style02', 'tamizo', 'sarajevo',
            'tokyolandscape', 'waji', 'tdnht', 'iwayan22', 'bird79',
            'plusneko', 'kengochi', 'kentarow', 'extrahot', 'getsukikyu',
            'hatch081', 'etocom', 'hamadahideaki', 'kotoributa', 'puti_towa',
            'szknm', 'taaaaan', 'almireanu', 'ellery', 'dcpndsgn', 'yucaringo',
            'Yu_mateto', 'photographgt', 'hatomie',
            ]

        session = get_current_session()
        session['access_token'] = access_token
        session['user']         = user

        if session.has_key('redirect_to'):
            self.redirect(session['redirect_to'])
            del(session['redirect_to'])
            return
        else:
            return self.redirect('/')

def main():
    app = webapp.WSGIApplication([
        ('/auth', AuthHandler),
        ],
        debug=False)
    app = SessionMiddleware(app, cookie_key='-\x9e}f\xd0h\x8fn\x83\x9a\xef\xf2\x13c\x15\x9cZk\x1f\x1d.Z\x02\xec\x8d)\xb9\r,\xb3\x90mG\x1a\xe2z\x9d\xb8\xd8d\xb6\x1a\xce\x81\x12\x89\xbdT\xf0c\x0e\x13N\xff\xfd\x9d\xc5\x87\xcd\xa3\xb6Y\xd6\x8f')
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)

if __name__ == "__main__":
  main()
