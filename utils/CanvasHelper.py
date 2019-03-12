from canvasapi import Canvas
import json
import numpy as np

# @TODO: change to IKI environment (UvA)

### SETUP ###
# Canvas API URL
API_URL = open('api_url.txt', 'r').readlines()[0].strip()
# Canvas API key
API_KEY = open('api_key.txt', 'r').readlines()[0].strip()
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Course ID (can be found in URL)
course = canvas.get_course(70)

" Returns list with all student average scores (ignoring ungraded assignments)"
# @TODO: get weight of assignment using assignment_id, add to dict
def current_scores(course):
    course_grades = {}
    for enr in course.get_enrollments():
        if enr.type == 'StudentEnrollment':
            course_grades[enr.sis_user_id] = enr.grades['current_score']

    return course_grades


" Creates bins for histogram plot of grades. Finds correct student assignment."
def frequency_count(gradedict, student_id, nr_bins=10, minn=0.0, maxx=100.0):
    ret = []
    data = []
    binsize = (maxx - minn) / float(nr_bins)
    #construct bins
    for x in range(0, nr_bins):
        start = minn + x * binsize
        ret.append([start, start+binsize, 0])
        data.append({'bucket':int(((start+(start+binsize))/2)) ,'size':0})
    #assign items to bin
    for item in list(gradedict.values()):
        for i,binn in enumerate(ret):
            if binn[0] <= item < binn[1]:
                    data[i]['size'] += 1
            if binn[0] <= gradedict[student_id] < binn[1]:
                student_bucket = data[i]['bucket']

    data.append({'assignment':student_bucket})
    return data


" Returns desired sigma (for Gaussian plot) based on completion"
def get_sigma(completion, minn=2, maxx=.4):
    if completion <= .1:
        return minn
    elif completion >.1 and completion < .75:
        return np.abs(1-completion)*minn + np.abs(completion-1)*maxx
    elif completion >= .75:
        return maxx

" Returns user data for both barplot and Gaussian plot"
def get_data(student):
    # Calculate all current scores (ignoring ungraded assignments)
    current_score = current_scores(course)

    # Calculate and save data for bar plot
    # @TODO: dynamically select user ID
    student = list(current_score.keys())[0]
    bardata = frequency_count(current_score, student)

    # Calculate and save data for Gauss plot
    grade = current_score[student]
    # weights = {'W1WG2':.1, 'W2WG2':.1, 'W3WG1':.1, 'W5WG1':.1, 'W6WG1':.1, 'W7WG1':.1, 'P1':.1, 'P2':.1, 'SAM':.1, 'POS':.1, 'DT1':.25, 'DT2':.25}
    # @TODO: dynamically set completion
    completion = .7
    gaussdata = {"weighted_grade":current_score[student]/10,"completion":completion, "sigma":get_sigma(completion)}

    return {"bardata": bardata, "gaussdata": gaussdata}

" Returns if user has given consent to use his/her data for visual"
def given_consent(student_id):
    consent = None
    for quizz in course.get_quizzes():
        for resp in quizz.get_all_quiz_submissions():
            if resp['user_id'] == student_id:
                if resp['score'] == 0.0:
                    consent = False
                elif resp['score'] == 1.0:
                    consent = True
    return consent
