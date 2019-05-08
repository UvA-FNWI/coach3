import pandas as pd
import numpy as np
from iki.models import User
from canvasapi import Canvas

API_URL = open('api_url.txt', 'r').readlines()[0].strip()
# Canvas API key
API_KEY = open('api_key.txt', 'r').readlines()[0].strip()
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def create_training_set(n_assessments):
    # todo: change position of presentation assignments accordingly to the release date of the grade
    data2018 = pd.read_csv("grades2018.csv")
    data2017 = pd.read_csv("grades2017.csv")
    data2019 = pd.read_csv("grades2017.csv")

    data = np.append(np.append(data2018.values, data2017.values, 0), data2019.values, 0)
    train_grades = data[:, -1]


    train_data = data[:, 1:n_assessments+1]

    return train_data, train_grades

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


def get_av_goal_data(user: User) -> pd.DataFrame:
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    users = course.get_users(enrollment_type='student')
    # print(len(users))
    av_goal_df = pd.DataFrame(columns=['av', 'goal'])

    # TODO: Get the goal grade from the assignment asking the student for a goal grade, instead of in the db
    for u in users:
        students = User.objects.filter(lti_id=u.id)
        if students.count() >0:
            student = student[0]
            av_goal_df = av_goal_df.append({'av': student.av_grade, 'goal': student.goal_grade}, ignore_index=True)

    # return av_goal_df
    # use dummy data for test phase
    return get_dummy_data()

def get_av_goal_data_true(user: User) -> pd.DataFrame:
    return

def get_dummy_data():
    goal_data = pd.read_csv('goal_grade.csv')
    print(goal_data)
    return goal_data


