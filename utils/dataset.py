import pandas as pd
import numpy as np


def create_set(grades_df):
    # todo: change position of presentation assignments accordingly to the release date of the grade
    data2018 = pd.read_csv("grades2018.csv")
    data2017 = pd.read_csv("grades2017.csv")
    data2019 = pd.read_csv("grades2017.csv")

    data = np.append(np.append(data2018.values, data2017.values, 0), data2019.values, 0)
    train_grades = data[:, -1]

    assessments_n = grades_df.shape[1]

    train_data = data[:, 1:assessments_n+1]

    return train_data, train_grades
