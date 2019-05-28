import pandas as pd
import numpy as np
from iki.models import User
from canvasapi import Canvas
from utils.AccessRights import can_use_data, load_access_file
from django.conf import settings

API_URL = open(settings.API_DIR+'api_url.txt', 'r').readlines()[0].strip()
# Canvas API key
API_KEY = open(settings.API_DIR+'api_key.txt', 'r').readlines()[0].strip()
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def create_training_set(n_assessments):
    """
    Loads the previous years grades and final grades from csv files and turns it into trainable data
    :param n_assessments: how many assignments have been graded so far for a user
    :return: train_data containing the historical assignment grades, train_grades containing the historical final grades.
    """
    # todo: change position of presentation assignments accordingly to the release date of the grade
    data2018 = pd.read_csv(settings.FILES_DIR+"grades2018.csv")
    data2017 = pd.read_csv(settings.FILES_DIR+"grades2017.csv")
    data2019 = pd.read_csv(settings.FILES_DIR+"grades201.csv")

    data = np.append(np.append(data2018.values, data2017.values, 0), data2019.values, 0)
    train_grades = data[:, -1]


    train_data = data[:, 1:n_assessments+1]

    return train_data, train_grades

def get_goals():
    """
    Get the goal grades of students in the course who gave consent to sharing it.
    :return: a dataframe containing the email (to identify the user), and goal grade of the students in the course.
    """
    data = load_access_file()
    data = data[data['access']=='y']
    return data[['email', 'goal']]

def get_goal_for_student(email):
    """
    Get the goal grade of a specific student given his/her email address
    :param email: the email address of the student
    :return: the goal grade of the student
    """
    data = get_goals()
    return data[data['email']==email]['goal'].values[0]


def current_grade(course):
    """
    Get the average grade of all students in the course whose data can be used.
    :param course: the course from which to get the grades.
    :return: a dict with student_id as key and average grade as value.
    """
    assignments = course.get_assignments()
    users = course.get_users(enrollment_type='student')
    weighted_grade = {}

    for student in users:
        email = student.email
        if can_use_data(email):
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
    return weighted_grade


def get_av_goal_data(user: User) -> pd.DataFrame:
    """
    Generates a dataframe containing the goal grade and average grade of all the students in the course who gave consent.
    Note: In the test version, a dummy set is generated
    :param user: the subject in the course
    :return: a dataframe containing goal grades and average grades.
    """

    # TODO: Make the code more logial and put iki.Course as argument instead of iki.User

    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    users = course.get_users(enrollment_type='student')
    av_goal_df = pd.DataFrame(columns=['av', 'goal'])
    student_avs = current_grade(course)
    goal_grades = get_goals()

    # TODO: Get the goal grade from the assignment asking the student for a goal grade, instead of in the db
    for u in users:
        email = u.email
        if can_use_data(email):
            av_grade = student_avs[u.id]
            # assignments = u.get_assignments(course, kwargs={"search_term": 'goal'})
            # for assignment in assignments:
            #     if assignment.name == 'goal':
            #         submission_content = assignment.get_submission(u).body
            #         print(submission_content)
            #         if submission_content != None:
            #             number = int(submission_content)
            #             print(number)

            goal_grade = goal_grades[goal_grades['email']==email]['goal'].values[0]
            av_goal_df = av_goal_df.append({'av': av_grade, 'goal': goal_grade}, ignore_index=True)
    # print(av_goal_df)

    # return av_goal_df
    # use dummy data for test phase
    return get_dummy_data()


def get_av_goal_data_true(user: User) -> pd.DataFrame:
    return


def get_dummy_data():
    """
    Generates a dummy dataset from a csv file.
    :return: a dummy data frame.
    """
    goal_data = pd.read_csv(settings.FILES_DIR+'goal_grade.csv')
    # print(goal_data)
    return goal_data




