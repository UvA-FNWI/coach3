from django.template import loader
from django.shortcuts import redirect
from utils.CanvasHelper import get_data, do_update_db
import json
from iki.forms import GoalResetForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import User
from django.http import Http404


@csrf_exempt
def index(request, user_id):
    """
    This is the main view of the tool, which renders a personalized visualisation
    If the page was not redirected from iki_lti/launch, returns a 404 error
    :param request: a dict of a post request
    :param user_id: the id of the user for which the visualisation will be rendered
    :return: render the page with context data
    """

    student_id = user_id

    students = User.objects.filter(iki_user_id=student_id)
    if students.count() > 0:
        student = students[0]
    else:
        raise ValueError("There is no student for the given user id")

    comparison_group = student.comparison_group
    has_comparison_group = student.has_comparison_group

    # See whether student has given consent
    #consent = given_consent(student)
    # consent=True

    # if 'pp_redarekt' in request.session:
    if True:

        # if consent:
        template = loader.get_template('iki/visuals.html')
        # Obtain data using CanvasHelper get_data function and send to html
        # del request.session['pp_redarekt']
        return render(request, 'iki/visuals.html', context={'data':json.dumps(get_data(student)),
                                                            'student_id': student_id,
                                                            "has_comparison_group": has_comparison_group})

        # elif consent == False:
        #     template = loader.get_template('iki/consent_false.html')
        #     return HttpResponse(template.render())
        #
        # elif consent == None:
        #     template = loader.get_template('iki/content_unknown.html')
        #     return HttpResponse(template.render(), student_id)

    raise Http404

def new_goal(request, student_id):
    """
    Used if a new goal needs to be set, for a certain user
    :param request: a POST request
    :param student_id: the id of the student for which the goal is changed
    :return: redirects to the main page.
    """
    user = User.objects.filter(iki_user_id=student_id)[0]
    if request.method == "POST":
        form_data = GoalResetForm(request.POST)
        # print(form_data)
        if form_data.is_valid():
            new_goal_grade = form_data.cleaned_data["new_goal_grade"]

            user.goal_grade = float(new_goal_grade)
            user.save()
            do_update_db(student_id)
            # set_goal_grade(new_goal_grade, student_id)
        else:
            print("post data not valid")
            messages.add_message(request, messages.ERROR, 'Please enter a valid goal grade')
    # set_goal_grade()

    # return redirect("iki:index", {'user_id': user.iki_user_id})
    return redirect("iki:index", user_id=student_id)

