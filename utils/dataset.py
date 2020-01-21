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


def create_training_set(n_assessments, graded_assignments_names):
    """
    Loads the previous years grades and final grades from csv files and turns it into trainable data
    :param n_assessments: how many assignments have been graded so far for a user
    :return: train_data containing the historical assignment grades, train_grades containing the historical final grades.
    """
    # todo: change position of presentation assignments accordingly to the release date of the grade
    data2018 = pd.read_csv(settings.FILES_DIR+"grades2018.csv")
    data2017 = pd.read_csv(settings.FILES_DIR+"grades2017.csv")
    data2019 = pd.read_csv(settings.FILES_DIR+"grades2019.csv")

    # data = np.append(np.append(data2018.values, data2017.values, 0), data2019.values, 0)
    # data = np.append(data2018.values, data2017.values, 0)
    # train_grades = data[:, -1]

    data = pd.concat([data2018, data2017], ignore_index=True)
    train_data = data[graded_assignments_names].values
    train_grades = data['Eindcijfer'].values

    return train_data, train_grades

def get_goals():
    """
    Get the goal grades of students in the course who gave consent to sharing it.
    :return: a dataframe containing the email (to identify the user), and goal grade of the students in the course.
    """
    data = load_access_file()
    data = data[data['access']=='y']
    return data[['name', 'goal']]

def get_goal_for_student(email, name):
    """
    Get the goal grade of a specific student given his/her email address
    :param email: the email address of the student
    :return: the goal grade of the student
    """
    data = get_goals()
    # if email.lower() in data['email'].values:
    #     return data[data['email']==email.lower()]['goal'].values[0]
    if name in data['name'].values:
        return data[data['name']==name]['goal'].values[0]
    else:
        raise ValueError("{} and {} do not fit any student in database".format(email, name))



def current_grade(course):
    """
    Get the average grade of all students in the course whose data can be used.
    :param course: the course from which to get the grades.
    :return: a dict with student_id as key and average grade as value.
    """

    if str(course.course_code) == "5082INKI6Y" or course.course_code == 'DamienTest':
        return current_grade_iki(course)

    assignments = course.get_assignments()
    users = course.get_users(enrollment_type='student')
    weighted_grade = {}

    for student in users:
        email = student.email
        name = student.name
        if can_use_data(email, name):
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
            else:
                weighted_grade[student.id] = 0
    return weighted_grade

def current_grade_iki(course):
    assignments = course.get_assignments()
    users = course.get_users(enrollment_type='student')
    weighted_grade = {}
    assignment_weights = pd.read_csv(settings.FILES_DIR+"assignments_weights_iki.csv")

    for student in users:
        # email = student.email
        name = student.name
        if can_use_data(name):
            total_weight = 0
            grade = 0
            so_weight = 0
            so_weighted_grade = 0
            is_final_so_graded = False
            for assignment in assignments:
                if assignment.get_submission(student).score:
                    assignment_name = assignment.name
                    if assignment_name in assignment_weights['Name'].values:
                        weight = assignment_weights[assignment_weights['Name']==assignment_name]['Weight'].values[0]
                        total_weight += weight
                        if assignment_name == 'Schrijfopdracht - 1e versie':
                            so_weighted_grade = float(assignment.get_submission(student).grade)*5*weight
                            so_weight = weight
                            grade += so_weighted_grade

                        else:
                            if assignment_name == 'Schrijfopdracht - Eindversie':
                                is_final_so_graded = True
                            grade += float(assignment.get_submission(student).grade)* weight
            if total_weight > 0:
                if is_final_so_graded:
                    weighted_grade[student.id] = (grade-so_weighted_grade)/(total_weight-so_weight)
                else:
                    weighted_grade[student.id] = grade/total_weight
            else:
                weighted_grade[student.id] = 0
    return weighted_grade

def get_graded_assignments_name(user: User):
    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    student = course.get_user(user.iki_user_id)
    assignments = course.get_assignments()
    graded_assignments = []

    for assignment in assignments:
        if assignment.get_submission(student).score and assignment.name != 'Schrijfopdracht - 1e versie':
            graded_assignments.append(assignment.name)

    return graded_assignments


def get_av_goal_data(user: User) -> pd.DataFrame:
    """
    Generates a dataframe containing the goal grade and average grade of all the students in the course who gave consent.
    Note: In the test version, a dummy set is generated
    :param user: the subject in the course
    :return: a dataframe containing goal grades and average grades.
    """


    course_id = user.course.iki_course_id
    course = canvas.get_course(course_id)
    users = course.get_users(enrollment_type='student')
    av_goal_df = pd.DataFrame(columns=['av', 'goal'])
    # student_avs = current_grade(course)
    student_avs = current_grade(course)
    goal_grades = get_goals()

    for u in users:
        # email = u.email
        name = u.name
        if can_use_data(name):
            av_grade = student_avs[u.id]
            # assignments = u.get_assignments(course, kwargs={"search_term": 'goal'})
            # for assignment in assignments:
            #     if assignment.name == 'goal':
            #         submission_content = assignment.get_submission(u).body
            #         print(submission_content)
            #         if submission_content != None:
            #             number = int(submission_content)
            #             print(number)

            goal_grade = goal_grades[goal_grades['name']==name]['goal'].values[0]
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




