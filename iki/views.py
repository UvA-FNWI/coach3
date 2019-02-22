from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from utils.CanvasHelper import get_data, given_consent
import json
from django_app_lti.views import LTILaunchView
from django.conf import settings
from django.core.urlresolvers import reverse


LTI_SETUP = settings.LTI_SETUP
INITIALIZE_MODELS = LTI_SETUP.get('INITIALIZE_MODELS', False)

def index(request, resource_id):
    # @TODO: add "get_all_quiz_submissions" function to canvasapi when deploying on server

    # @TODO: get student id dynamically (using LTI / request)
    #@TODO: use this student id for visual (i.e. sent to .html)

    student_id = 506

    # See whether student has given consent
    consent = given_consent(student_id)

    if consent:
        template = loader.get_template('iki/visuals.html')
        # Obtain data using CanvasHelper get_data function and send to html
        return render(request, 'iki/visuals.html', context={'data':json.dumps(get_data())})

    elif consent == False:
        template = loader.get_template('iki/consent_false.html')
        return HttpResponse(template.render())

    elif consent == None:
        template = loader.get_template('iki/content_unknown.html')
        return HttpResponse(template.render())


# class MyLTILaunchView(LTILaunchView):
#     def hook_get_redirect(self):
#         '''
#         Returns a redirect for after the POST request.
#         '''
#         launch_redirect_url = LTI_SETUP['LAUNCH_REDIRECT_URL']
#         kwargs = None
#         if self.lti_resource is not None:
#             kwargs = {"resource_id": self.lti_resource.id}
#         return redirect(reverse('iki:index', kwargs=kwargs))
