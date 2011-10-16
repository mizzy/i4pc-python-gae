from google.appengine.ext import db

class Feed(db.Model):
    user      = db.StringProperty()
    user_id   = db.StringProperty()
    sessionid = db.StringProperty()
    feed_id   = db.StringProperty()

class Photo(db.Model):
    photo_id = db.IntegerProperty()
    data     = db.TextProperty()

    
