from helper import timestamp_to_datetime

class ApiModel(object):

    @classmethod
    def object_from_dictionary(cls, entry):
        # make dict keys all strings
        #entry_str_dict = dict([(str(key), value) for key,value in entry.items()])
        #return cls(**entry_str_dict)
        return entry
    
class Image(ApiModel):
    
    def __init__(self, url, width, height):
        self.url = url
        self.height = height
        self.width = width

class Media(ApiModel):

    def __init__(self, id=None, **kwargs):
        self.id = id
        for key,value in kwargs.iteritems():
            setattr(self, key, value)
    
    def get_standard_resolution_url(self):
        return self.images['standard_resolution'].url
    
    @classmethod
    def object_from_dictionary(cls, entry):
        new_media = Media(id=entry['id'])
        
        new_media.user = entry['user']
        new_media.images = {}
        for version,version_info in entry['images'].iteritems():
            new_media.images[version] = Image(**version_info)

        if 'user_has_liked' in entry:
            new_media.user_has_liked = entry['user_has_liked']
        new_media.like_count = entry['likes']['count']
        if entry['likes']['count'] == True:
            new_media.like_count = 1
            
        new_media.comment_count = entry['comments']['count']
        if entry['comments']['count'] == True:
            new_media.comment_count = 1
            
        new_media.comments = []
        for comment in entry['comments']['data']:
            new_media.comments.append(Comment.object_from_dictionary(comment))

        new_media.created_time = timestamp_to_datetime(entry['created_time'])

        if entry['location']:
            new_media.location = Location.object_from_dictionary(entry['location'])

        new_media.link    = entry['link']
        new_media.caption = entry['caption']
        
        return new_media

class Tag(ApiModel):
    def __init__(self, name, **kwargs):
        self.name = name
        for key,value in kwargs.iteritems():
            setattr(self, key, value)
        
    def __str__(self):
        return "Tag %s" % self.name

class Comment(ApiModel):
    def __init__(self, *args, **kwargs):
        for key,value in kwargs.iteritems():
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        user = entry['from']
        text = entry['text']
        created_at = timestamp_to_datetime(entry['created_time'])
        id = entry['id']
        return {
            'id'        : id,
            'user'      : user,
            'text'      : text,
            'created_at': created_at,
            }

    def __unicode__(self):
        print "%s said \"%s\"" % (self.user.username, self.message)

class Point(ApiModel):
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class Location(ApiModel):
    def __init__(self, id, *args, **kwargs):
        self.id = id
        for key,value in kwargs.iteritems():
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        point = None
        if entry.has_key('latitude'):
            point = Point(entry['latitude'],
                          entry['longitude'])

        id = None
        if entry.has_key('id'):
            id = entry['id']

        name = None
        if entry.has_key('name'):
            name = entry['name']

        return {
            'id'   : id,
            'point': point,
            'name' : name,
            }

class User(ApiModel):

    def __init__(self, id, *args, **kwargs):
        self.id = id
        for key,value in kwargs.iteritems():
            setattr(self, key, value)

    def __str__(self):
        return "User %s" % self.username

class Relationship(ApiModel):

    def __init__(self, incoming_status="none", outgoing_status="none"):
        self.incoming_status = incoming_status
        self.outgoing_status = outgoing_status
        

