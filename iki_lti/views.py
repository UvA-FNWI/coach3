from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

import enum

from iki_lti import factory
from iki.models import User
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from ims_lti_py.tool_config import ToolConfig
from django.views.generic import View
import urllib.request, urllib.parse, urllib.error
from django.http import HttpResponse, HttpResponseRedirect
# from braces.views import CsrfExemptMixin




LTI_SETUP = settings.LTI_SETUP
INITIALIZE_MODELS = LTI_SETUP.get('INITIALIZE_MODELS', False)


class LTI_STATES(enum.Enum):
    """VUE ENTRY STATE."""
    KEY_ERR = '-2'
    BAD_AUTH = '-1'

    NO_USER = '0'
    LOGGED_IN = '1'

    NO_COURSE = '0'
    NO_ASSIGN = '1'
    NEW_COURSE = '2'
    NEW_ASSIGN = '3'
    FINISH_T = '4'
    FINISH_S = '5'


@csrf_exempt
def lti_launch(request):
    """Django view for the lti post request.

    Verifies the given LTI parameters based on our secret. If the user does not
    yet exist, and is allowed to interact with the tool, a new user is created.
    The page is then redirected to the index page.

    """

    secret = settings.LTI_SECRET
    key = settings.LTI_KEY

    # try:
    #     factory.OAuthRequestValidater.check_signature(key, secret, request)
    # except (oauth2.Error, ValueError):
    #     return redirect(factory.create_lti_query_link(QueryDict.fromkeys(['state'], LTI_STATES.BAD_AUTH.value)))
    factory.OAuthRequestValidater.check_signature(key, secret, request)

    launch_redirect_url = LTI_SETUP['LAUNCH_REDIRECT_URL']
    params = request.POST.dict()
    lti_user_id = params['user_id']
    users = User.objects.filter(lti_id=lti_user_id)

    if users.count() > 0:
        user = users[0]
        return redirect("iki:index", user_id=user.iki_user_id)
    else:
        user = User.create_user(params)
        print('launch student id')
        print(type(user.iki_user_id))
    # return redirect("iki:index", user_id=user.iki_user_id)
    return redirect("iki:index", user_id=user.iki_user_id)




class LTIToolConfigView(View):
    LAUNCH_URL = LTI_SETUP.get('LAUNCH_URL', 'lti:launch')
    """
    Outputs LTI configuration XML for Canvas as specified in the IMS Global Common Cartridge Profile.

    The XML produced by this view can either be copy-pasted into the Canvas tool
    settings, or exposed as an endpoint to Canvas by linking to this view.
    """
    def get_launch_url(self, request):
        '''
        Returns the launch URL for the LTI tool. When a secure request is made,
        a secure launch URL will be supplied.
        '''
        if request.is_secure():
            host = 'https://' + request.get_host()
        else:
            host = 'http://' + request.get_host()
        url = host + reverse(self.LAUNCH_URL)
        return self._url(url);

    def set_ext_params(self, lti_tool_config):
        '''
        Sets extension parameters on the ToolConfig() instance.
        This includes vendor-specific things like the course_navigation
        and privacy level.

        EXAMPLE_EXT_PARAMS = {
            "canvas.instructure.com": {
                "privacy_level": "public",
                "course_navigation": {
                    "enabled": "true",
                    "default": "disabled",
                    "text": "MY tool (localhost)",
                }
            }
        }
        '''
        EXT_PARAMS = LTI_SETUP.get("EXTENSION_PARAMETERS", {})
        for ext_key in EXT_PARAMS:
            for ext_param in EXT_PARAMS[ext_key]:
                ext_value = EXT_PARAMS[ext_key][ext_param]
                lti_tool_config.set_ext_param(ext_key, ext_param, ext_value)

    def get_tool_config(self, request):
        '''
        Returns an instance of ToolConfig().
        '''
        launch_url = self.get_launch_url(request)
        return ToolConfig(
            title=LTI_SETUP['TOOL_TITLE'],
            description=LTI_SETUP['TOOL_DESCRIPTION'],
            launch_url=launch_url,
            secure_launch_url=launch_url,
        )

    def get(self, request, *args, **kwargs):
        '''
        Returns the LTI tool configuration as XML.
        '''
        lti_tool_config = self.get_tool_config(request)
        self.set_ext_params(lti_tool_config)
        return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml', status=200)

    def _url(self, url):
        '''
        Returns the URL with the resource_link_id parameter removed from the URL, which
        may have been automatically added by the reverse() method. The reverse() method is
        patched by django-auth-lti in applications using the MultiLTI middleware. Since
        some applications may not be using the patched version of reverse(), we must parse the
        URL manually and remove the resource_link_id parameter if present. This will
        prevent any issues upon redirect from the launch.
        '''
        parts = urllib.parse.urlparse(url)
        query_dict = urllib.parse.parse_qs(parts.query)
        if 'resource_link_id' in query_dict:
            query_dict.pop('resource_link_id', None)
        new_parts = list(parts)
        new_parts[4] = urllib.parse.urlencode(query_dict)
        return urllib.parse.urlunparse(new_parts)
