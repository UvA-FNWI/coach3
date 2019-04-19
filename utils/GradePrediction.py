import numpy as np
import math
import pandas as pd
from typing import List
import pprint


conf_int = 10
q = 0.1
bigK = 11
weights = [5/108, 5/108, 5/108, 5/108, 1/4, 5/108, 5/108, 5/108, 5/108, 1/6, 1/4]


class Neighbor:
    def __init__(self, feat_vector: List[float], dist: float):
        self.feat_vector = feat_vector
        self.dist = dist


class Neighborhood:
    def __init__(self, neighbors: List[Neighbor], r):
        self.neighbors = neighbors
        self.r = r


#  formula (17)
def vector_distance(student1: List[float], student2: List[float], weights) -> float:
    """
    Assesses the distance between two students
    :param student1: feature vector of the target student
    :param student2: feature vector of the peer student
    :return: the distance between the two students as formulated in (17)
    """

    assert(len(student1)==len(student2)), \
        "The size of the feature vectors don't match. Student1: %r, Student2: %r" % (len(student1), len(student2))
    assert(len(student1)==len(weights)), \
        "The length of the weight vector does not match the feature vectors. Weights: %r, feature vector %r" \
        % (len(weights), len(student1))

    upper = 0
    lower = np.sum(weights)
    for x1, x2, w in zip(student1, student2, weights):
        upper += w*abs(x1-x2)
    return upper/lower


def make_neighborhoods(student: List[float], group, k):
    """

    :param student: feature_vector of the target student
    :param group: list of the feature vectors of students from previous years
    :return: a list of Neighborhood objects
    """
    neighborhoods = []
    neighbors = []
    for member in group:
        neighbor = Neighbor(member, vector_distance(student[:k], member[:k], weights[:k]))
        neighbors.append(neighbor)
    sorted_neighbors = np.array(sorted(neighbors, key=lambda n: n.dist))

    def make_neighborhoods_help(sorted_neighbors, index, r):
        new_index = index
        new_r = r
        if index == 0:
            new_index = 3
        while new_index + 1 < len(sorted_neighbors) and sorted_neighbors[new_index].dist <= r:
            new_index += 1
        if sorted_neighbors[new_index].dist > r + 0.1:
            new_r = sorted_neighbors[new_index].dist
        else:
            new_r = r + 0.1
        if new_index > index:
            return new_index, new_r
        else:
            make_neighborhoods_help(sorted_neighbors, new_index + 1, new_r)

    r = 0.1
    i = 0
    while i < len(sorted_neighbors)-1:
        i, r = make_neighborhoods_help(sorted_neighbors, i, r)
        neighborhoods.append(Neighborhood(sorted_neighbors[:i], sorted_neighbors[i].dist))
    return neighborhoods


# formula (1)
def calculate_score(assessments: List[float]) -> float:
    """
    calculates the overall or residual score of a student based on their number of assessments and their weights
    :param assessments: an array of the score of all assessments
    :return: the score of the student
    """
    score = 0
    for i in range(0, len(assessments)):
        score += assessments[i]*weights[i]
    return score


# formula (5)
def estimate_residual(neighborhood: Neighborhood, k: int) -> float:
    """
    Estimates the residual of a neighborhood
    :param neighborhood: list of instances of Neighbor
    :param k: current assessment time
    :return: the residual as formulated in (5)
    """
    upper = 0
    lower = len(neighborhood.neighbors)
    for neighbor in neighborhood.neighbors:
        upper += calculate_score(neighbor.feat_vector[k:])

    return upper/lower


# formula (7)
def estimate_var(neighborhood: Neighborhood, k: int) -> float:
    """
    Estimates the variance of a neighborhood
    :param neighborhood: list of instances of Neighbor
    :param k: current assessment time
    :return: the variance of the neighborhood as formulated in (7)
    """
    upper = 0
    lower = len(neighborhood.neighbors) - 1
    est_residual = estimate_residual(neighborhood, k)
    for neighbor in neighborhood.neighbors:
        residual = calculate_score(neighbor.feat_vector[k:])
        upper += math.pow(residual - est_residual, 2)

    return upper/lower


# formula (8)
def prediction_confidence(est_var: float) -> float:
    """
    Deerives the confidence from the estimated variance
    :param est_var: Estimated variance
    :return:
    """
    return 1 - est_var/(conf_int*conf_int)


def find_w_largest_pred_conf(neighborhoods: List[Neighborhood]) -> Neighborhood:
    """
    Find the neighborhood with the larges prediction confidence
    :param neighborhoods: list of instances of Neighborhood
    :return: the best Neighborhood
    """
    # m = np.argmax(neighborhood.q for neighborhood in neighborhoods)
    m = np.argmin(neighborhood.est_var for neighborhood in neighborhoods)
    # print("neighborhood radius:", neighborhoods[m].r, end='\t\t')
    # print()
    # for neighbor in neighborhoods[m].neighbors:
    #     print(neighbor.feat_vector)
    # pprint(neighbor.feat_vector for neighbor in neighborhoods[m].neighbors)
    return neighborhoods[m]


def is_confidence_ok(pred_conf: float) -> bool:
    """
    Checks the confidence of a Neighborhood against a criterion q
    :param pred_conf: the confidence of the neighborhood
    :return: True if the confidence is good, False otherwise
    """
    return pred_conf >= q


def compute_est_final(assessments: List[float], est_residual: float, k: int) -> float:
    """
    Estimates the final grade of the target student
    :param assessments: a list of all the assessment grades up until now (i.e. k)
    :param est_residual: the estimated residual for the target student
    :param k: the current assessment time
    :return: the estimated final grade
    """
    return calculate_score(assessments[:k]) + est_residual





# formula (16)
def standardize_scores(scores):
    standardized = []
    mean_score = np.mean(scores)
    sd_score = np.std(scores)
    # print('sd:', sd_score, '\tmean:', mean_score)
    for score in scores:
        new_score = (score - mean_score)/sd_score
        standardized.append(new_score)
    return standardized


data2018 = pd.read_csv("grades2018.csv")
data2017 = pd.read_csv("grades2017.csv")

# convert the dataframe into an array and remove the id column and final grade column
data_val2018 = data2018.values[:, :-1]
data_val2017 = data2017.values[:, 1:-1]
# convert the dataframe into an array and remove the id column and final grade column
data_val2018 = data2018.values[:, :-1]
data_val2017 = data2017.values[:, 1:-1]

final_grades = np.append(data2018.values[:, -1], data2017.values[:, -1])
mean = np.mean(final_grades)
sd = np.std(final_grades)
print('sd:', sd)
print('mean:', mean)

np.random.shuffle(data_val2018)
np.random.shuffle(data_val2017)


test_amount = math.floor(0.05*len(data_val2018))

test_data = data_val2018[:test_amount, 1:]
test_ids = data_val2018[:test_amount, 0]

data_val2018 = data_val2018[test_amount:, 1:]


st_data_val2018 = []
for i, col in enumerate(data_val2018.T):
    # data_val2018.T[i, :] = standardize_scores(col)
    st_data_val2018.append(standardize_scores(col))
st_data_val2018 = np.array(st_data_val2018).T

st_data_val2017 = []
for i, col in enumerate(data_val2017.T):
    # data_val2017.T[i, :] = standardize_scores(col)
    st_data_val2017.append(standardize_scores(col))
st_data_val2017 = np.array(st_data_val2017).T

st_test_data = []
for i, col in enumerate(test_data.T):
    # means.append(np.mean(col))
    # sd.append(np.std(col))
    st_test_data.append(standardize_scores(col))
st_test_data = np.array(st_test_data).T

train_data = np.append(data_val2018, data_val2017, 0)
st_train_data = np.append(st_data_val2018, st_data_val2017, 0)


def get_prediction(student: List[float]) -> (float, float):
    """
    Predicts the final grade of a student based on their current grades
    :param student: the grades of the student so far
    :return: estimated variance, estimated mean
    """
    if not student:
        return 0, 0

    k = len(student)
    if k == bigK:
        return 0, calculate_score(student)
    neighborhoods = make_neighborhoods(student, train_data, k)
    for neighborhood in neighborhoods:
        neighborhood.est_res = estimate_residual(neighborhood, k)
        neighborhood.est_var = estimate_var(neighborhood, k)
        neighborhood.q = prediction_confidence(neighborhood.est_var)
    candidate = find_w_largest_pred_conf(neighborhoods)

    if is_confidence_ok(candidate.q):
        return candidate.est_var, compute_est_final(student, candidate.est_res, k)
    else:
        return 0, 0


