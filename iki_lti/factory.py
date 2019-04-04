from datetime import datetime, timezone

import oauth2
from django.conf import settings


class OAuthRequestValidater(object):
    """OAuth request validater class for Django Requests"""

    def __init__(self, key, secret):
        """
        Constructor which creates a consumer object with the given key and
        secret.
        """
        super(OAuthRequestValidater, self).__init__()
        self.consumer_key = key
        self.consumer_secret = secret

        self.oauth_server = oauth2.Server()
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()
        self.oauth_server.add_signature_method(signature_method)
        self.oauth_consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)

    def parse_request(self, request):
        """
        Parses a django request to return the method, url, header and post data.
        """
        return request.method, request.build_absolute_uri(), request.META, request.POST.dict()

    def is_valid(self, request):
        """
        Checks if the signature of the given request is valid based on the
        consumers secret en key
        """
        method, url, head, param = self.parse_request(request)
        oauth_request = oauth2.Request.from_request(method, url, headers=head, parameters=param)
        self.oauth_server.verify_request(oauth_request, self.oauth_consumer, {})

    @classmethod
    def check_signature(cls, key, secret, request):
        """Validate OAuth request using the python-oauth2 library.

        https://github.com/simplegeo/python-oauth2.
        """
        validator = OAuthRequestValidater(key, secret)
        validator.is_valid(request)


def create_lti_query_link(query):
    """
    Creates link to lti page with the given parameters
    Arguments
    query -- QueryDict of the query variables
    returns the link
    """
    return ''.join((settings.BASELINK, '/LtiLogin', '?', query.urlencode()))
