from canvasapi import Canvas
# from utils.Grade_prediction import predict
import json
import numpy as np
import pandas as pd
# from utils.GradePrediction import get_prediction
from utils.bayesian import get_prediction
from utils.dataset import create_set
# from iki.tasks import test, update_db
from background_task import background
from iki.models import Course, User
import random


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

def frequency_count_comp(grades, user_grade, nr_bins=20, minn=0.0, maxx=10.0):
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
    for item in grades:
        for i, binn in enumerate(ret):
            if item is not None and binn[0] <= item < binn[1]:
                    data[i]['size'] += 1
            # sets aside the student grade in another student_bucket
            # NOTE: the student grade is still included in the general bucket
            # as it will be included in the average grade calculation
            if binn[0] <= user_grade < binn[1]:
                student_bucket = data[i]['bucket']

    data.append({'assignment': student_bucket})
    return data

def set_goal_grade(goal, student_id):
    user = User.objects.filter(iki_user_id=student_id)[0]
    user.goal_grade = goal
    user.save()
    make_comparison_group(goal)

def make_comparison_group(user):
    # alternatively, get the goal grade from the "body" attribute from the submission for an assignment in which we ask
    # for the goal grade. And couple that with the current_score function to get the average-goal tuple
    goal = user.goal_grade
    average = user.av_grade
    course = user.course
    users = course.get_users(enrollment_type='student')
    av_goal_df = pd.DataFrame(columns=['av', 'goal'])
    for u in users:
        av_goal_df = av_goal_df.append({'av':u.av_grade, 'goal':u.goal_grade}, ignore_index=True)

    def get_same_goal_set(student_data, size, goal_grade):
        """
        Creates a set of students in a course who have similar goal grades (within a defined range) as the user
        :param student_data: a dataframe containing the average grade and the goal grade of every student
        :type: pd.DataFrame
        :param size: the minimal size of the set
        :param goal_grade: the goal grade of the user
        :return: a list of the average grades of the students having the same-ish goal grade as the user and the size of
        the window used. If no set of size ≥ the desired size, return an empty list
        """
        peers = []
        window = 0.1
        # candidates = student_data
        candidates = student_data.sample(frac=1)
        # candidates = random.shuffle(student_data)

        #adds students who have set goal grade ± window to the peers list and removes them from the candidates list. If,
        # for a set window, not enough peers have been found, increase the size of the window and redo the loop.
        while len(peers) < size:
            # note: at the first iteration of the while loop, len(peer) can be > 40. That means that in the first iteration,
            # we take all students whose goals are equal to the given goal±window

            for i, n in candidates.iterrows():
                # print(n['goal'])
                if goal_grade - window <= (n['goal']) <= goal_grade + window:
                    peers.append(n)
                    candidates = candidates.drop(i)
            window += 0.1
            if window > 0.3:
                return [], window
        return peers, window

    def make_comparison_set(start_set, end_set, mean, set_size):
        """
        From a set of students with similar goals, makes a comparison set, such that the grand average grade of the set
        is equal to mean and the size of the set is set_size
        :param start_set: the set of students with similar goals
        :param end_set: the comparison set to be returned
        :param mean: the grand average grade that the comparison set must have
        :param set_size: the size of the comparison set
        :return: end_set, aka the comparison set. If no comparison set has been found, returns a set of zeros
        """

        # assert len(end_set == 7), "The size of the end set is too small. Must contain 7 elements"

        if round(np.mean(end_set), 2) == mean and len(end_set) == set_size:
            return end_set

        # assert len(start_set) > 0, "Could not find a subset from the set given"
        if len(start_set) == 0:
            return np.zeros(7)

        end_set = np.append(end_set, start_set[0])
        start_set = start_set[1:]

        if round(np.mean(end_set), 2) > mean:
            max_indices = end_set.argsort()[-3:]
            max_index = np.argmax(end_set)
            end_set = np.delete(end_set, max_index)
        elif round(np.mean(end_set), 2) < mean:
            min_indices = end_set.argsort()[3:]
            min_index = np.argmin(end_set)
            end_set = np.delete(end_set, min_index)
        return make_comparison_set(start_set, end_set, mean, set_size)

    def dist_from_top(peers, average):
        dist = len([peer for peer in peers['av'] if peer>average])
        return dist

    def dist_from_bottom(peers, average):
        dist = len([peer for peer in peers['av'] if peer < average])
        return dist

    def get_special_set(peers, isTop, size):
        avs = np.sort(peers['av'])
        if isTop:
            return avs[-size:]
        return avs[:size]

    def get_set(average, goal_grade, av_goal_df, set_size):
        for i in range(10, 50):
            peers, w = get_same_goal_set(av_goal_df, i, goal_grade)
            if len(peers) == 0:
                return np.zeros(set_size)#, w, [], False
            av = peers['av'].values
            for j in range(0, 100):
                random.shuffle(av)
                start_set = np.array(av)[7:]
                end_set = np.array(av)[:7]
                set = make_comparison_set(start_set, end_set, average, set_size)
                if np.sum(set) > 0:
                    return set#, w, av, True
                #accounts for special cases in which the user is either in the top 2 or bottom 2 of the cohort
                elif dist_from_top(peers, average)<2:
                    set = get_special_set(peers,True, set_size)
                    return set#, w, av, True
                elif dist_from_bottom(peers, average) < 2:
                    set = get_special_set(peers, False, set_size)
                    # return set, w, av, True
        return np.zeros(set_size)#, w, av, False

    group = get_set(average+1, goal, av_goal_df, 7)
    if np.sum(group) > 0:
        user.has_comparison_group = True
    else:
        user.has_comparison_group = False
    group_as_frequency = frequency_count_comp(group, average)
    user.comparison_group = group_as_frequency
    user.save()


@background()
def update_db(student_id):
    user = User.objects.filter(iki_user_id=student_id)[0]
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    grades = get_user_scores(course, user)


    if user.assessments != grades.values.shape[1]:
        user.assessments = grades.values.shape[1]
        user.grades = grades.values.tostring()
        print('updating student', student_id)
        print(grades)

        # current_score = current_scores(course)
        current_score = current_grade(course)
        # Calculate and save data for bar plot

        if current_score[student_id] is None:
            current_score[student_id] = 0
        print('current score')
        print(current_score)

        user.av_grade = current_score[student_id]
        # print('av grade:', current_score[student_id])

        bardata = frequency_count(current_score, student_id)
        print('bardata')
        print(bardata)
        user.comparison_group = json.dumps(bardata)

        train_data, train_grades = create_set(grades)
        est_grade, est_sd = get_prediction(grades.values, train_data, train_grades)
        user.grade_pred = est_grade
        user.grade_sigma = est_sd
        user.save()
    print('task done')


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
    update_db(student_id)
    est_grade = user.grade_pred
    est_sd = user.grade_sigma
    gaussdata = {"weighted_grade": est_grade, "sigma": est_sd}
    comparison_groups = user.comparison_group
    if comparison_groups is None:
        current_score = current_grade(course)
        if not student_id in current_score.keys():
            current_score[student_id] = 0
        print(current_score)
        comparison_groups = frequency_count(current_score, student_id)
        return {"bardata": comparison_groups, "gaussdata": gaussdata, "student_name": student_name}
    bardata = json.loads(comparison_groups)

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

