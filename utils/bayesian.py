from sklearn.linear_model import BayesianRidge
import numpy as np


def get_prediction(course_grades, train_data, train_grades):
    model = BayesianRidge()
    model.fit(train_data, train_grades)
    y_mean, y_sd = model.predict(np.array(course_grades).reshape(1, -1), return_std=True)

    return y_mean, y_sd
