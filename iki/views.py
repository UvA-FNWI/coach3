from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from utils.CanvasHelper import get_data, given_consent
import json
from django.conf import settings
from django.core.urlresolvers import reverse

import enum

from iki import factory
from .models import User
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from ims_lti_py.tool_config import ToolConfig
from django.views.generic import View
import urllib.request, urllib.parse, urllib.error
from django.http import HttpResponse, HttpResponseRedirect
from braces.views import CsrfExemptMixin
from django.shortcuts import render, get_object_or_404
from .models import User



@csrf_exempt
def index(request, user_id):
    # @TODO: add "get_all_quiz_submissions" function to canvasapi when deploying on server

    # @TODO: get student id dynamically (using LTI / request)
    # @TODO: use this student id for visual (i.e. sent to .html)

    student_id = user_id

    students = User.objects.filter(iki_user_id=student_id)
    if students.count() > 0:
        student = students[0]
    else:
        raise ValueError("There is no student for the given user id")

    # See whether student has given consent
    #consent = given_consent(student)
    consent=True

    if consent:
        template = loader.get_template('iki/visuals.html')
        # Obtain data using CanvasHelper get_data function and send to html
        return render(request, 'iki/visuals.html', context={'data':json.dumps(get_data(student))})

    elif consent == False:
        template = loader.get_template('iki/consent_false.html')
        return HttpResponse(template.render())

    elif consent == None:
        template = loader.get_template('iki/content_unknown.html')
        return HttpResponse(template.render())
