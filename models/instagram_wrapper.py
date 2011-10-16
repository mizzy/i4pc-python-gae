# -*- coding: utf-8 -*-
import sys
import os
sys.path.append('../lib')
from instagram.client import InstagramAPI
import re
from google.appengine.api import memcache
import emoji
from xml.sax.saxutils import escape

if re.match('Development', os.environ['SERVER_SOFTWARE']):
    CLIENT_ID     = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    CLIENT_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    REDIRECT_URI  = 'http://127.0.0.1:8080/auth'
else:
    CLIENT_ID     = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    CLIENT_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    REDIRECT_URI  = 'http://www.i4pc.jp/auth'

class Instagram():
    def __init__(self):
        self.api = InstagramAPI(
            client_id     = CLIENT_ID,
            client_secret = CLIENT_SECRET,
            redirect_uri  = REDIRECT_URI,
            )

    def set_access_token(self, access_token):
        self.api = InstagramAPI(
            access_token = access_token
            )
        
    def media_popular(self, **params):
        popular = memcache.get('popular_feed')
        if not popular:
            popular = self.api.media_popular(count=params['count'], max_id=params['max_id'])
            memcache.add('popular_feed', popular, 300)
        return popular

    def user_media_feed(self, **params):
        user_id = params['user_id']
        max_id  = params['max_id']
        count   = params['count']

        feed = memcache.get('user_media_feed_%s_%s' % ( user_id, max_id ) )
        if not feed:
            feed = self.api.user_media_feed(count=count, max_id=max_id)
            memcache.add('user_media_feed_%s_%s' % ( user_id, max_id ), feed, 300 )
        return feed

    def user_liked_feed(self, **params):
        user_id = params['user_id']
        max_id  = params['max_id']
        count   = params['count']
        feed = memcache.get('user_liked_feed_%s_%s' % ( user_id, max_id ) )
        if not feed:
            feed = self.api.user_liked_feed(count=count, max_like_id=max_id)
            memcache.add('user_liked_feed_%s_%s' % ( user_id, max_id ), feed, 300 )
        return feed
    
    def user(self, user_id):
        user = memcache.get('user_%s'% ( user_id ))
        if not user:
            user = self.api.user(user_id)
            user['full_name'] = escape(user['full_name'].encode('utf-8'))
            user['full_name'] = self._convert_emoji(user['full_name'])
            memcache.add('user_%s' % ( user_id ), user, 300)
        return user

    def media(self, media_id):
        media = memcache.get('media_%s' % media_id)
        if not media:
            media = self.api.media(media_id)
            media.user['full_name'] = escape(media.user['full_name'].encode('utf-8'))
            media.user['full_name'] = self._convert_emoji(media.user['full_name'])
            if media.caption:
                media.caption['text_original'] = media.caption['text']
                media.caption['text'] = escape(media.caption['text'].encode('utf-8'))
                media.caption['text'] = self._convert_emoji(media.caption['text'])
                media.caption['text'] = self._convert_tag_to_link(media.caption['text'])
            memcache.add('media_%s' % media_id, media, 300)
        return media

    def media_comments(self, media_id):
        comments = memcache.get('media_comments_%s'% ( media_id ))
        if not comments:
            converter = emoji.factory('softbank', 'utf-8')
            converter.prefix = '<span class="emoji emoji_'
            converter.suffix = '"></span>'
            comments = self.api.media_comments(media_id)
            for comment in comments:
                comment['text'] = escape(comment['text'].encode('utf-8'))
                comment['text'] = self._convert_emoji(comment['text'])
                comment['text'] = self._convert_tag_to_link(comment['text'])
            memcache.add('media_comments_%s' % ( media_id ), comments, 300)
        return comments

    def media_likes(self, media_id):
        likes = memcache.get('media_likes_%s' % ( media_id ))
        if not likes:
            likes = self.api.media_likes(media_id)
            memcache.add('media_likes_%s' % ( media_id ), likes, 300)
        return likes

    def user_recent_media(self, **params):
        user_id = params['user_id']
        max_id  = params['max_id']
        feed = memcache.get('user_recent_media_%s_%s' % (user_id, max_id))
        if not feed:
            feed = self.api.user_recent_media(user_id=user_id, max_id=max_id)
            memcache.add('user_recent_media_%s_%s' % (user_id, max_id), feed, 300)
        return feed

    def user_follows(self, **params):
        user_id = params['user_id']
        count   = params['count']
        cursor  = params['cursor']
        follows = memcache.get('user_follows_%s_%s_%s' % (user_id, count, cursor))
        if not follows:
            follows = self.api.user_follows(user_id=user_id, count=count, cursor=cursor)
            for user in follows[0]:
                user['full_name'] = escape(user['full_name'].encode('utf-8'))
                user['full_name'] = self._convert_emoji(user['full_name'])
            memcache.add('user_follows_%s_%s_%s' % (user_id, count, cursor), follows, 300)
        return follows

    def user_followed_by(self, **params):
        user_id = params['user_id']
        count   = params['count']
        cursor  = params['cursor']
        follows = memcache.get('user_followed_by_%s_%s_%s' % (user_id, count, cursor))
        if not follows:
            follows = self.api.user_followed_by(user_id=user_id, count=count, cursor=cursor)
            for user in follows[0]:
                user['full_name'] = escape(user['full_name'].encode('utf-8'))
                user['full_name'] = self._convert_emoji(user['full_name'])
            memcache.add('user_followed_by_%s_%s_%s' % (user_id, count, cursor), follows, 300)
        return follows

    def like_media(self, **params):
        user_id  = params['user_id']
        media_id = params['media_id']
        max_id   = params['max_id']
    
        self.api.like_media(media_id)
        memcache.add('user_has_liked_%s_%s' % ( user_id, media_id ), True, 300)
        memcache.delete('media_likes_%s' % ( media_id ))
        
    def unlike_media(self, **params):
        user_id  = params['user_id']
        media_id = params['media_id']
        max_id   = params['max_id']
    
        self.api.unlike_media(media_id)
        memcache.delete('user_has_liked_%s_%s' % ( user_id, media_id ))
        memcache.delete('media_likes_%s' % ( media_id ))

    def create_media_comment(self, **params):
        media_id = params['media_id']
        text     = params['text']
        self.api.create_media_comment(
            media_id = media_id,
            text     = text,
            )
        memcache.delete('media_%s' % media_id)
        memcache.delete('media_comments_%s' % media_id)
        
    def user_find_by_username(self, username):
        user = memcache.get( 'user_find_by_username_%s' % ( username ) )

        if not user:
            users = self.api.user_search(q=username, count=None)
            for u in users:
                if username == u['username']:
                    user = u
                    memcache.add( 'user_find_by_username_%s' % ( username ), user )

        return user

    def tag_recent_media(self, **params):
        tag_name = params['tag_name']
        count    = params['count']
        max_id   = params['max_id']

        feed = memcache.get('tag_recent_media_%s_%s' % ( tag_name, max_id ) )

        if not feed:
            feed = self.api.tag_recent_media(
                tag_name = tag_name,
                count    = count,
                max_id   = max_id,
                )
            memcache.add('tag_recent_media_%s_%s' % ( tag_name, max_id ), feed, 300)

        return feed

    def get_authorize_login_url(self, **params):
        uri = memcache.get('authorize_login_uri')
        if not uri:
            uri = self.api.get_authorize_login_url(
                scope = params['scope']
                )
            memcache.add('authorize_login_uri', uri, 300)
        return uri
    
    def _convert_emoji(self, text):
        converter = emoji.factory('softbank', 'utf-8')
        converter.prefix = '<span class="emoji emoji_'
        converter.suffix = '"></span>'
        text = converter.convert(text)
        return text

    def _convert_tag_to_link(self, text):
        text = re.sub(r'#([a-zA-Z0-9\-]+)', '<a href="/tag/\g<1>">#\g<1></a>', text)
        return text

    def relationship(self, **params):
        owner_id = params['owner_id']
        my_id    = params['my_id']

        relationship = memcache.get('relationship_%s_%s' % ( my_id, owner_id ))
        if not relationship:
            relationship = self.api.relationship(owner_id)
            memcache.add('relationship_%s_%s' % ( my_id, owner_id ), relationship, 300)

        return relationship

    def follow_user(self, **params):
        owner_id = params['owner_id']
        my_id    = params['my_id']

        relationship = self.api.follow_user(user_id=owner_id)
        memcache.delete('relationship_%s_%s' % ( my_id, owner_id ))
        return relationship
    
    def unfollow_user(self, **params):
        owner_id = params['owner_id']
        my_id    = params['my_id']

        relationship = self.api.unfollow_user(user_id=owner_id)
        memcache.delete('relationship_%s_%s' % ( my_id, owner_id ))
        return relationship

