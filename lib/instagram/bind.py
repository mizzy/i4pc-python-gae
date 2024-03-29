import urllib
from oauth2 import OAuth2Request
import re
import simplejson
import yaml

re_path_template = re.compile('{\w+}')

def encode_string(value):
    return value.encode('utf-8') \
                        if isinstance(value, unicode) else str(value)

class InstagramClientError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        return self.error_message

class InstagramAPIError(Exception):
    
    def __init__(self, status_code, error_type, error_message, *args, **kwargs):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return "(%s) %s-%s" % (self.status_code, self.error_type, self.error_message)

def bind_method(**config):

    class InstagramAPIMethod(object):

        path = config['path']
        method = config.get('method', 'GET')
        accepts_parameters = config.get("accepts_parameters", [])
        requires_target_user = config.get('requires_target_user', False)
        paginates = config.get('paginates', False)
        root_class = config.get('root_class', None)
        response_type = config.get("response_type", "list")

        def __init__(self, api, *args, **kwargs):
            self.api = api
            self.as_generator = kwargs.pop("as_generator", False)
            self.max_pages = kwargs.pop("max_pages", 3)
            self.parameters = {}
            self._build_parameters(args, kwargs)
            self._build_path() 

        def _build_parameters(self, args, kwargs):
            # via tweepy https://github.com/joshthecoder/tweepy/
            for index, value in enumerate(args):
                if value is None:
                    continue

                try:
                    self.parameters[self.accepts_parameters[index]] = encode_string(value)
                except IndexError:
                    raise InstagramClientError("Too many arguments supplied")

            for key, value in kwargs.iteritems():
                if value is None:
                    continue
                if key in self.parameters:
                    raise InstagramClientError("Parameter %s already supplied" % key)
                self.parameters[key] = encode_string(value)
            if 'user_id' in self.accepts_parameters and not 'user_id' in self.parameters \
               and not self.requires_target_user:
                self.parameters['user_id'] = 'self'

        def _build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                try:
                    value = urllib.quote(self.parameters[name])
                except KeyError:
                    raise Exception('No parameter value found for path variable: %s' % name)
                del self.parameters[name]

                self.path = self.path.replace(variable, value)
            self.path = self.path + '.%s' % self.api.format

        def _do_api_request(self, url, method="GET", body=None, headers={}):
            response, content = OAuth2Request(self.api).make_request(url, method=method, body=body, headers=headers)
            if response['status'] == '503':
                raise InstagramAPIError(response['status'], "Rate limited", "Your client is making too many request per second")
            #content_obj = simplejson.loads(content)
            content_obj = yaml.load(content)
            response_objects = []
            status_code = content_obj['meta']['code']
            if status_code == 200:
                if self.response_type == 'list':
                    for entry in content_obj['data']:
                        obj = self.root_class.object_from_dictionary(entry)
                        response_objects.append(obj)
                elif self.response_type == 'entry':
                    response_objects = self.root_class.object_from_dictionary(content_obj['data'])
                return response_objects, content_obj.get('pagination', {})
            else:
                raise InstagramAPIError(status_code, content_obj['meta']['error_type'], content_obj['meta']['error_message'])

        def _paginator_with_url(self, url, method="GET", body=None, headers={}):
            pages_read = 0
            while url and pages_read < self.max_pages:
                 response_objects, url = self._do_api_request(url, method, body, headers)
                 pages_read += 1
                 yield response_objects, url 
            return

        def execute(self):
            url, method, body, headers = OAuth2Request(self.api).prepare_request(self.method, self.path, self.parameters)
            if self.as_generator:
                return self._paginator_with_url(url, method, body, headers)
            else:
                content, next = self._do_api_request(url, method, body, headers)
            if self.paginates:
                return content, next
            else:
                return content


    def _call(api, *args, **kwargs):
        method = InstagramAPIMethod(api, *args, **kwargs)
        return method.execute()

    return _call
