from sklearn.linear_model import BayesianRidge
import numpy as np


def get_prediction(course_grades, train_data, train_grades):
    """
    Predicts the final grade of a student given his/her grades so far, using Bayesian Linear Regression
    :param course_grades: the grades obtained so far by a student in the course
    :param train_data: the training set of values
    :param train_grades: the training set of targets
    :return:
    """

    # In the case the student has no grade, return a predicted grade of 0
    if train_data.size == 0:
        return 0,0

    model = BayesianRidge()
    model.fit(train_data, train_grades)
    y_mean, y_sd = model.predict(np.array(course_grades).reshape(1, -1), return_std=True)

    return y_mean, y_sd
