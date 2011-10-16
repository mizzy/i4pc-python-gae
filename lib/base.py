import os
from google.appengine.ext.webapp import template
import logging

def set_template(action):
    path = os.path.join(os.path.dirname(__file__), '../templates/' + action + '.html')
    return path

def format_date(dt):
    """convert a datetime into an RFC 822 formatted date

    Input date must be in GMT.
    """
    # Looks like:
    #   Sat, 07 Sep 2002 00:00:01 GMT
    # Can't use strftime because that's locale dependent
    #
    # Isn't there a standard way to do this for Python?  The
    # rfc822 and email.Utils modules assume a timestamp.  The
    # following is based on the rfc822 module.
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
            dt.day,
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month-1],
            dt.year, dt.hour, dt.minute, dt.second)

def error(handler, code=500, message=None):
    if message:
        logging.error(message + ': ' + handler.request.path)
    path = set_template('error')
    handler.response.set_status(code)
    handler.response.out.write(template.render(path, {
        'message': message,
        'path'   : handler.request.path,
        }))
    return
