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


@csrf_exempt
def index(request, user_id):
    # @TODO: add "get_all_quiz_submissions" function to canvasapi when deploying on server

    # @TODO: use this student id for visual (i.e. sent to .html)

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
    consent=True

    if consent:
        template = loader.get_template('iki/visuals.html')
        # Obtain data using CanvasHelper get_data function and send to html
        return render(request, 'iki/visuals.html', context={'data':json.dumps(get_data(student)),
                                                            'student_id': student_id,
                                                            "has_comparison_group": has_comparison_group})

    elif consent == False:
        template = loader.get_template('iki/consent_false.html')
        return HttpResponse(template.render())

    elif consent == None:
        template = loader.get_template('iki/content_unknown.html')
        return HttpResponse(template.render(), student_id)

def new_goal(request, student_id):
    # set_goal_grade(new_goal_grade,student_id)
    user = User.objects.filter(iki_user_id=student_id)[0]
    if request.method == "POST":
        form_data = GoalResetForm(request.POST)
        # print(form_data)
        if form_data.is_valid():
            new_goal_grade = form_data.cleaned_data["new_goal_grade"]
            print("new goal grade:", new_goal_grade)

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

