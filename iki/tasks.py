# # Create your tasks here
# from background_task import background
# from utils.CanvasHelper import frequency_count, create_set, current_grade
# from utils.bayesian import get_prediction
# import json
#
# #####
#
# # @background()
# # def test():
# #     print('test')
#
# @background()
# def update_db(student_id, grades, course):
#
#     if user.assessments != grades.values.shape[1]:
#         user.assessments = grades.values.shape[1]
#         user.grades = grades.values.tostring()
#         print(grades)
#
#         # current_score = current_scores(course)
#         current_score = current_grade(course)
#         # Calculate and save data for bar plot
#
#         if current_score[student_id] is None:
#             current_score[student_id] = 0
#
#         user.av_grade = current_score[student_id]
#         print('av grade:', current_score[student_id])
#
#
#
#         bardata = frequency_count(current_score, student_id)
#         user.comparison_group = json.dumps(bardata)
#
#         train_data, train_grades = create_set(grades)
#         est_grade, est_sd = get_prediction(grades.values, train_data, train_grades)
#         # print(est_grade[0], est_sd)
#         gaussdata = {"weighted_grade": est_grade[0], "sigma": est_sd[0]}
#         user.grade_pred = est_grade
#         user.grade_sigma = est_sd
#         user.save()