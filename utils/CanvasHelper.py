from canvasapi import Canvas
# from utils.Grade_prediction import predict
import json
import numpy as np
import pandas as pd
# from utils.GradePrediction import get_prediction
from utils.bayesian import get_prediction
from utils.dataset import create_set
from iki.task import add


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
                total_weight = float(course.get_assignment_group(assignment_id).group_weight)
                grade += float(assignment.get_submission(student).grade)*total_weight
        if total_weight > 0:
            weighted_grade[student.id] = grade/total_weight
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


def frequency_count(gradedict, student_id, nr_bins=10, minn=0.0, maxx=100.0):
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
        data.append({'bucket': int(((start+(start+binsize))/2)), 'size': 0})
        # QUESTION: why do we need the ret array?
    # assign items to bin
    for item in list(gradedict.values()):
        for i, binn in enumerate(ret):
            if item is not None and binn[0] <= item < binn[1]:
                    data[i]['size'] += 1
            # sets aside the student grade in another student_bucket
            # NOTE: the student grade is still included in the general bucket
            # as it will be included in the average grade calculation
            if binn[0] <= gradedict[student_id] < binn[1]:
                student_bucket = data[i]['bucket']

    data.append({'assignment': student_bucket})
    return data


def get_sigma(completion, minn=2, maxx=.4):
    " Returns desired sigma (for Gaussian plot) based on completion"
    if completion <= .1:
        return minn
    elif completion > .1 and completion < .75:
        return np.abs(1-completion)*minn + np.abs(completion-1)*maxx
    elif completion >= .75:
        return maxx


def get_data(user):
    """
    Returns user data for both barplot and Gaussian plot
    Calculate all current scores (ignoring ungraded assignments)
    :param user: A User object representing the student interacting with the tool.
    :return: A JSON format including the necessary data to draw the comparison diagram and the grade prediction diagram.
    """

    # Calculate all current scores (ignoring ungraded assignments)"
    add.delay(8,7)

    course_id = user.course.iki_course_id
    student_id = user.iki_user_id
    course = canvas.get_course(course_id)
    grades = get_user_scores(course, user)

    student_name = user.name


    # dummy_scores = [7.,  7.,  5., 7., 6.5]
    # est_var, est_grade = get_prediction(dummy_scores)

    if user.assessments != grades.values.shape[1]:
        user.assessments = grades.values.shape[1]
        user.grades = grades.values.tostring()
        print(grades)

        # current_score = current_scores(course)
        current_score = current_grade(course)
        # Calculate and save data for bar plot

        if current_score[student_id] is None:
            current_score[student_id] = 0

        user.av_grade = current_score[student_id]
        print('av grade:', current_score[student_id])



        bardata = frequency_count(current_score, student_id)
        user.comparison_group = json.dumps(bardata)

        train_data, train_grades = create_set(grades)
        est_grade, est_sd = get_prediction(grades.values, train_data, train_grades)
        # print(est_grade[0], est_sd)
        gaussdata = {"weighted_grade": est_grade[0], "sigma": est_sd[0]}
        user.grade_pred = est_grade
        user.grade_sigma = est_sd
        user.save()
    else:
        est_grade = user.grade_pred
        est_sd = user.grade_sigma
        gaussdata = {"weighted_grade": est_grade, "sigma": est_sd}
        bardata = json.loads(user.comparison_group)

    return {"bardata": bardata, "gaussdata": gaussdata, "student_name": student_name}


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
