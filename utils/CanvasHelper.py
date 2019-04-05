from canvasapi import Canvas
# from utils.Grade_prediction import predict
import json
import numpy as np
from utils.GradePrediction import get_prediction


# @TODO: change to IKI environment (UvA)

### SETUP ###
# Canvas API URL
API_URL = open('api_url.txt', 'r').readlines()[0].strip()
# Canvas API key
API_KEY = open('api_key.txt', 'r').readlines()[0].strip()
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Course ID (can be found in URL)


def current_scores(course):
    " Returns list with all student average scores (ignoring ungraded assignments)"
    # @TODO: get weight of assignment using assignment_id, add to dict
    course_grades = {}
    for enr in course.get_enrollments():
        if enr.type == 'StudentEnrollment':
            course_grades[enr.user_id] = enr.grades['current_score']
    return course_grades

def get_user_scores(course, userid):
    grades = []
    return current_scores(course)[userid]


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
    """ Returns user data for both barplot and Gaussian plot
    Calculate all current scores (ignoring ungraded assignments)
    """
    # Calculate all current scores (ignoring ungraded assignments)"

    course_id = user.course.iki_course_id
    student_id = user.iki_user_id
    course = canvas.get_course(course_id)
    current_score = current_scores(course)

    # Calculate and save data for bar plot
    if current_score[student_id] is None:
        current_score[student_id] = 0

    bardata = frequency_count(current_score, student_id)
    student_name = user.name

    # Calculate and save data for Gauss plot
    grade = current_score[student_id]
    # weights = {'W1WG2':.1, 'W2WG2':.1, 'W3WG1':.1, 'W5WG1':.1, 'W6WG1':.1, 'W7WG1':.1, 'P1':.1, 'P2':.1, 'SAM':.1, 'POS':.1, 'DT1':.25, 'DT2':.25}
    completion = .7
    # gaussdata = {"weighted_grade": current_score[student_id]/10, "completion": completion, "sigma": get_sigma(completion)}

    dummy_scores = [7.,  7.,  5., 7., 6.5]
    est_var, est_grade = get_prediction(dummy_scores)
    # est_var, est_grade = get_prediction(current_scores[student_id])
    gaussdata = {"weighted_grade": est_grade, "sigma": est_var}

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
