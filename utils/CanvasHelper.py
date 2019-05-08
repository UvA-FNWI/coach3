from canvasapi import Canvas
import json
import numpy as np
import pandas as pd
from utils.bayesian import get_prediction
from utils.dataset import create_training_set
from background_task import background
from iki.models import User
from utils.ComparisonGroupFactory import make_comparison_group
import reversion


# @TODO: change to IKI environment (UvA)

### SETUP ###
# Canvas API URL
API_URL = open('api_url.txt', 'r').readlines()[0].strip()
# Canvas API key
API_KEY = open('api_key.txt', 'r').readlines()[0].strip()
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def current_scores(course):
    """
    Deprecated, use current_grade instead.
    :param course:
    :return:
    """
    " Returns list with all student average scores (ignoring ungraded assignments)"
    # @TODO: get weight of assignment using assignment_id, add to dict
    course_grades = {}
    for enr in course.get_enrollments():
        if enr.type == 'StudentEnrollment':
            course_grades[enr.user_id] = enr.grades['current_score']
            # print(enr.grades['current_score'])

    return course_grades


def current_grade(course):
    assignments = course.get_assignments()
    users = course.get_users(enrollment_type='student')
    weighted_grade = {}

    for student in users:
        total_weight = 0
        grade = 0
        for assignment in assignments:
            if assignment.grading_type == 'gpa_scale' and assignment.get_submission(student).grade:
                assignment_id = assignment.assignment_group_id
                weight = float(course.get_assignment_group(assignment_id).group_weight)
                total_weight += weight
                grade += float(assignment.get_submission(student).grade)*weight
        if total_weight > 0:
            weighted_grade[student.id] = grade/total_weight
    print(weighted_grade)
    return weighted_grade


def get_user_scores(course, user):

    # todo: grades are currently sorted by groups assignment (alphabetically) and then by date within the group.
    #  Find a way such that it is ordered only by release date.
    assignments = course.get_assignments()
    grades = pd.DataFrame()
    student_id = user.iki_user_id
    # poster = 0

    # poster_release_week = 0
    assessments = 0
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
        elif assignment.get_submission(student_id).grade:
            grades[assignment.name] = [float(assignment.get_submission(student_id).grade)]
            # grades.append(float(assignment.get_submission(student_id).grade))
            assessments += 1
        # print(assignment.grading_type)


    return grades
    # return grades


def frequency_count(gradedict, student_id, nr_bins=20, minn=0.0, maxx=10.0):
    " Creates bins for histogram plot of grades. Finds correct student assignment."
    ret = []
    data = []
    binsize = (maxx - minn) / float(nr_bins)
    student_bucket = []
    # construct bins
    # each bin consist of a start position and end position and a zero value(?)
    # QUESTION: why the null value?
    # each bin represents a grade on the x-axis
    # bins are stored in the ret variable
    for x in range(0, nr_bins):
        start = minn + x * binsize
        ret.append([start, start+binsize, 0])
        data.append({'bucket': start+binsize, 'size': 0})
        # QUESTION: why do we need the ret array?
    # assign items to bin
    for item in list(gradedict.values()):
        for i, binn in enumerate(ret):
            if item is not None and binn[0] <= item < binn[1]:
                    data[i]['size'] += 1
            # sets aside the student grade in another student_bucket
            # NOTE: the student grade is still included in the general bucket
            # as it will be included in the average grade calculation
            if student_id in gradedict.keys():
                if binn[0] <= gradedict[student_id] < binn[1]:
                    student_bucket = data[i]['bucket']
            else: student_bucket = 0

    data.append({'assignment': student_bucket})
    return data





def update_db(student_id):
    user = User.objects.filter(iki_user_id=student_id)[0]
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    grades = get_user_scores(course, user)

    if user.assessments != grades.shape[1]:
        do_update_db(student_id)
    print('task done')

def do_update_db(student_id):
    user = User.objects.filter(iki_user_id=student_id)[0]
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    grades = get_user_scores(course, user)

    with reversion.create_revision():
        user.assessments = grades.shape[1]
        # user.grades = ','.join(str(x) for x in [str(i) for i in grades.values])
        print('updating student', student_id)
        print(grades)

        # current_score = current_scores(course)
        current_score = current_grade(course)
        # Calculate and save data for bar plot
        print('current score')
        print(int(student_id) in current_score.keys())
        if int(student_id) not in current_score.keys():
            current_score[int(student_id)] = 0
        print('current score')
        print(current_score)

        user.av_grade = current_score[int(student_id)]
        # print('av grade:', current_score[student_id])

        # make_comparison_group(user)
        # comparison_group, has_comparison = make_set_for_diagram(user)
        comparison_group, has_comparison, solution_mean, solution_std, solution_mean_distance = make_comparison_group(
            user)
        print(has_comparison, solution_mean, solution_std, solution_mean_distance)
        user.comparison_group = json.dumps(comparison_group)
        print('before')
        print(json.dumps(comparison_group))
        print(type(comparison_group))
        print('after')
        print(user.comparison_group)
        print(type(user.comparison_group))
        user.has_comparison_group = has_comparison
        user.comparison_distance_mean = solution_mean_distance
        user.comparison_mean = solution_mean
        user.comparison_std = solution_std

        # bardata = frequency_count(current_score, student_id)
        # print('bardata')
        # print(bardata)
        # user.comparison_group = json.dumps(bardata)

        # -----------------------------------------

        train_data, train_grades = create_training_set(grades.shape[1])
        est_grade, est_sd = get_prediction(grades.values, train_data, train_grades)
        user.grade_pred = est_grade
        user.grade_sigma = est_sd
        user.save()

        # reversion.set_user(request.user)
        reversion.set_comment("Created revision 1")

@background()
def general_db_update():
    users = User.objects.all()
    for user in users:
        update_db(user.iki_user_id)
    print('for all students')


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
    # todo: check that for 2 users the data is updated for both
    # for student in course.get_users(enrollment_type='student'):
    #     print(student)
    #     print(vars(student))
    #     update_db(student.id, repeat=60)
    # update_db(student_id)
    est_grade = user.grade_pred
    est_sd = user.grade_sigma
    gaussdata = {"weighted_grade": est_grade, "sigma": est_sd}
    # comparison_groups = user.comparison_group
    if user.comparison_group =='nothing':
        # current_score = current_grade(course)
        # if not student_id in current_score.keys():
        #     current_score[student_id] = 0
        # comparison_groups = frequency_count(current_score, student_id)
        do_update_db(student_id)
    # bardata = json.loads(user.comparison_group)
    #     return {"bardata": comparison_groups, "gaussdata": gaussdata, "student_name": student_name}
    # print('comparison group')
    # print(comparison_groups)
    assert type(user.comparison_group) == str, 'the type of the user comparison is not str, it is {}'.format(type(user.comparison_group))
    bardata = json.loads(user.comparison_group)

    return {"bardata": bardata, "gaussdata": gaussdata}


def given_consent(user):
    " Returns if user has given consent to use his/her data for visual"
    consent = None
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    for quizz in course.get_quizzes():
        for resp in quizz.get_all_quiz_submissions():
            if resp['user_id'] == user.iki_user_id:
                if resp['score'] == 0.0:
                    consent = False
                elif resp['score'] == 1.0:
                    consent = True
    return consent

