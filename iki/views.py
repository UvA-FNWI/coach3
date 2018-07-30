from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from utils.CanvasHelper import get_data, given_consent
import json

def index(request):
    # @TODO: add "get_all_quiz_submissions" function to canvasapi when deploying on server

    # @TODO: get student id dynamically (using LTI / request)
    #@TODO: use this student id for visual (i.e. sent to .html)

    student_id = 506

    # See whether student has given consent
    consent = given_consent(student_id)


    # @TODO: (maybe) store data in db every n minutes? (So that not retrieved every time.)

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
