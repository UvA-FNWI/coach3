from canvasapi import Canvas
import json
import numpy as np
import pandas as pd
from utils.bayesian import get_prediction
from utils.dataset import create_training_set, current_grade, get_graded_assignments_name, get_goal_for_student
from background_task import background
from iki.models import User
from utils.ComparisonGroupFactory import make_comparison_group
import reversion
import datetime
from django.conf import settings


# @TODO: change to IKI environment (UvA)

### SETUP ###
# Canvas API URL
API_URL = open(settings.API_DIR+'api_url.txt', 'r').readlines()[0].strip()
# Canvas API key
API_KEY = open(settings.API_DIR+'api_key.txt', 'r').readlines()[0].strip()
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def get_user_scores(course, user):
    """
    get the grades of the students so far in a course
    :param course: the course to fetch the grades from. course is an instance of Canvas.Course
    :param user: the user for which to fetch the grades. user is an instance of Canvas.User
    :return: a dataframe with the names of the assignments as colums names and grades in the row.
    """

    # todo: grades are currently sorted by groups assignment (alphabetically) and then by date within the group.
    #  Find a way such that it is ordered only by release date.
    assignments = course.get_assignments()
    grades = pd.DataFrame()
    student_id = user.iki_user_id
    # poster = 0

    # poster_release_week = 0
    for assignment in assignments:
        attrs = vars(assignment)
        # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
        # now dump this in some way or another
        # print('\n'.join("%s: %s" % item for item in attrs.items()))
        # print(assignment.score)
        # print(assignment)

        if assignment.grading_type == "pass_fail":
            if assignment.get_submission(student_id).grade == 'incomplete':
                return []
        elif assignment.get_submission(student_id).grade and assignment.name != 'Schrijfopdracht - 1e versie':
            grades[assignment.name] = [float(assignment.get_submission(student_id).grade)]

    return grades





def update_db(student_id):
    """
    Updates the model of a student if her/his grade or number of assignments graded have changed
    :param student_id: the id of the student
    :return:
    """
    user = User.objects.filter(iki_user_id=student_id)[0]
    course_id = user.course.iki_course_id
    try:
        course = canvas.get_course(int(course_id))
    except ValueError:
        print('course id {} not found'.format(course_id))
    grades = get_user_scores(course, user)
    canvas_av = current_grade(course)
    goal = get_goal_for_student(user.email, user.name)

    if user.assessments != grades.shape[1] or canvas_av[user.iki_user_id] != float(user.av_grade) or user.goal_grade != goal:
        do_update_db(student_id)



def do_update_db(student_id):
    """
    A helper to the update_db function. Is called to perform the update.
    :param student_id: the id of the student
    :return:
    """
    user = User.objects.filter(iki_user_id=student_id)[0]
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    grades_and_names = get_user_scores(course, user)

    with reversion.create_revision():
        user.assessments = grades_and_names.shape[1]
        # user.grades = ','.join(str(x) for x in [str(i) for i in grades.values])
        print('updating student', student_id)
        print(grades_and_names)

        # current_score = current_scores(course)
        current_score = current_grade(course)
        graded_assignments = list(grades_and_names.columns)

        # Calculate and save data for bar plot
        if int(student_id) not in current_score.keys():
            print('student id not in score list')
            current_score[int(student_id)] = 0

        user.av_grade = current_score[int(student_id)]
        print('current score: {}'.format(current_score[int(student_id)]))

        comparison_group, has_comparison, solution_mean, solution_std, solution_mean_distance, edge_case = make_comparison_group(user, current_score[int(student_id)])

        user.comparison_group = json.dumps(comparison_group)
        user.has_comparison_group = has_comparison
        user.comparison_distance_mean = solution_mean_distance
        user.comparison_mean = solution_mean
        user.comparison_std = solution_std
        user.edge_case = edge_case

        train_data, train_grades = create_training_set(grades_and_names.shape[1], graded_assignments)
        est_grade, est_sd = get_prediction(grades_and_names.values, train_data, train_grades)
        user.grade_pred = est_grade
        user.grade_sigma = est_sd
        user.save()

        # reversion.set_user(request.user)
        reversion.set_comment("updated at {}".format(datetime.datetime.now()))

@background()
def general_db_update():
    """
    Calls update_db for all the student registered in the database.
    :return:
    """
    users = User.objects.all()
    for user in users:
        update_db(user.iki_user_id)
    print('task done at {}'.format(datetime.datetime.now()))


def get_data(user):
    """
    Returns user data for both barplot and Gaussian plot
    Calculate all current scores (ignoring ungraded assignments)
    :param user: A User object representing the student interacting with the tool.
    :return: A JSON format including the necessary data to draw the comparison diagram and the grade prediction diagram.
    """

    student_id = user.iki_user_id
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)

    student_name = user.name

    est_grade = user.grade_pred
    est_sd = user.grade_sigma
    gaussdata = {"weighted_grade": est_grade, "sigma": est_sd}
    if user.comparison_group =='nothing':
        do_update_db(student_id)

    assert type(user.comparison_group) == str, 'the type of the user comparison is not str, it is {}'.format(type(user.comparison_group))
    bardata = json.loads(user.comparison_group)
    # round the mean value of the comparison group to the closest .25/.75
    comp_curve = ({'comp_mean': round(user.comparison_mean * 4) / 4, 'comp_std': user.comparison_std})

    return {"bardata": bardata, "gaussdata": gaussdata, "comp_curve": comp_curve}


# def given_consent(user):
#     " Returns if user has given consent to use his/her data for visual"
#     consent = None
#     course_id = user.course.iki_course_id
#     course = canvas.get_course(course_id)
#     for quizz in course.get_quizzes():
#         for resp in quizz.get_all_quiz_submissions():
#             if resp['user_id'] == user.iki_user_id:
#                 if resp['score'] == 0.0:
#                     consent = False
#                 elif resp['score'] == 1.0:
#                     consent = True
#     return consent

