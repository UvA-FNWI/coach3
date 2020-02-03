from django.shortcuts import render, redirect
from django.conf import settings

from iki_lti import factory
from iki.models import User
from django.views.decorators.csrf import csrf_exempt
#from ims_lti_py.tool_config import ToolConfig
from rest_framework.decorators import api_view
from utils.AccessRights import has_access
from utils.dataset import get_goal_for_student
from enum import unique



LTI_SETUP = settings.LTI_SETUP
INITIALIZE_MODELS = LTI_SETUP.get('INITIALIZE_MODELS', False)


@csrf_exempt
@api_view(['POST'])
# @unique
def lti_launch(request):
    """Django view for the lti post request.

    Verifies the given LTI parameters based on our secret. If the user does not
    yet exist, and is allowed to interact with the tool, a new user is created.
    The page is then redirected to the index page.

    """

    secret = settings.LTI_SECRET
    key = settings.LTI_KEY

    factory.OAuthRequestValidater.check_signature(key, secret, request)

    launch_redirect_url = LTI_SETUP['LAUNCH_REDIRECT_URL']
    params = request.POST.dict()
    email = params['lis_person_contact_email_primary']
    name = params['lis_person_name_full']
    # if True:
    if has_access(email, name):
        lti_user_id = params['user_id']
        users = User.objects.filter(lti_id=lti_user_id)
        request.session['pp_redarekt'] = True

        if users.count() > 0:
            user = users[0]
            user.log_count += 1
            user.save()
            return redirect("iki:index", user_id=user.iki_user_id)
        else:
            params['goal'] = get_goal_for_student(email)
            user = User.create_user(params)
            return redirect("iki:index", user_id=user.iki_user_id)
    else:
        return render(request, 'iki/access_refused.html')
