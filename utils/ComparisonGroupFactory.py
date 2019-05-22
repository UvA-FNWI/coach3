from iki.models import User
import pandas as pd
import numpy as np
import random
from utils.dataset import get_av_goal_data, current_grade
import json
from utils.ComparisonBuckets import frequency_count_comp


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
    peers = pd.DataFrame(columns=['goal', 'av'])
    window = 0.01
    # candidates = student_data
    candidates = student_data.sample(frac=1)
    # candidates = random.shuffle(student_data)

    # adds students who have set goal grade ± window to the peers list and removes them from the candidates list. If,
    # for a set window, not enough peers have been found, increase the size of the window and redo the loop.
    while True:
    # while window <=0.2:
        # note: at the first iteration of the while loop, len(peer) can be > 40. That means that in the first iteration,
        # we take all students whose goals are equal to the given goal±window

        for i, n in candidates.iterrows():
            # print(n['goal'])
            if goal_grade - window <= (n['goal']) <= goal_grade + window:
                peers = peers.append(n, ignore_index=True)
                candidates = candidates.drop(i)
            if len(peers) >= size: break
        window += 0.01
        if len(peers) >= size:
            break
    return peers['av'].values, window


def make_comparison_set(start_set, end_set,average,l_b, u_b, set_size):
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
    better_peers = end_set[end_set > average]
    worse_peers = end_set[end_set < average]
    worse_eq_peers = end_set[end_set <= average]

    if average+l_b <= round(np.mean(end_set), 2) <= average+u_b and len(end_set) == set_size and \
            len(better_peers)>len(worse_eq_peers) and len(worse_peers)>=1 and len(worse_eq_peers)>=2:
        return end_set

    # assert len(start_set) > 0, "Could not find a subset from the set given"
    if len(start_set) == 0:
        return np.zeros(7)

    end_set = np.append(end_set, start_set[0])
    start_set = start_set[1:]

    if round(np.mean(end_set), 2) > u_b:
        max_indices = end_set.argsort()[-3:]
        max_index = np.argmax(end_set)
        end_set = np.delete(end_set, max_index)
    elif round(np.mean(end_set), 2) < l_b:
        min_indices = end_set.argsort()[3:]
        min_index = np.argmin(end_set)
        end_set = np.delete(end_set, min_index)
    return make_comparison_set(start_set, end_set, average, l_b, u_b, set_size)


def dist_from_top(peers, average):
    """
    Gives the rank of a student from the top
    :param peers: all the students in the course, for which we can use the data
    :param average: the average grade of the student
    :return: the position in the rank from the top
    """
    dist = len([peer for peer in peers['av'] if peer > average])
    return dist


def dist_from_bottom(peers, average):
    """
        Gives the rank of a student from the bottom
        :param peers: all the students in the course, for which we can use the data
        :param average: the average grade of the student
        :return: the position in the rank from the bottom
        """
    dist = len([peer for peer in peers['av'] if peer < average])
    return dist


def get_special_set(peers, average, isTop, isOther, size):
    """
    Retrieves a comparison set for edge cases. Edge cases are students for which the algorithm could not find any
    comparison set. It is the case for some students at the ends of the average grade distribution. If the student is
    within the top or the bottom of her/his class, the comparison set will be the top and bottom groups, respectfully.
    If the student is not part of the top. The comparison set will consist of 60% of the closest better peers and 40% of
    the closes worse peers.
    :param peers: An array containing the average grades of the whole cohort.
    :param average: The students average grade.
    :param isTop: True if the student is in the top of his/her class. False otherwise.
    :param isOther: True, if the student is neither in the top, nor the bottom. False otherwise.
    :param size: The desired size of the comparison set.
    :return: A comparison set.
    """
    avs = np.sort(peers['av'])
    if isTop:
        return avs[-size:]
    elif not isOther:
        return avs[:size]

    highers = avs[np.where(avs > average)]
    lowers = avs[np.where(avs <= average)]
    n_highers = np.round(size*0.6)
    n_lowers = size-n_highers
    comparison_set = np.append(lowers[-n_lowers:], highers[:n_highers])
    assert len(comparison_set) == 7, 'wrong size of set for edge case'
    return comparison_set


def get_set(average, goal_grade, av_goal_df, set_size):
    """
    General function that finds a comparison set for a given average, goal grade and size. Handles edge cases if no
    comparison could be found.
    :param average: the average grade of a student
    :param goal_grade: the goal grade of a student
    :param av_goal_df: a dataframe containing the average and goal grades of all students in the course who consented to
    share these data
    :param set_size: the size of the comparison set
    :return: the comparison set in the form of an array, the window from which the set was created, whether a solution
    has been found, and in which edge case (if any) the user falls in.
    """
    # solution = []
    for i in range(10, 50):
        peers, w = get_same_goal_set(av_goal_df, i, goal_grade)
        if len(peers) == 0:
            has_solution = False
            edge_case = 'error'
            return np.zeros(set_size), w, has_solution, edge_case
        for j in range(0, 100):
            random.shuffle(peers)
            start_set = peers[set_size:]
            end_set = peers[:set_size]
            solution = make_comparison_set(start_set, end_set, average, 0.5, 1.0, set_size)

            if np.sum(solution) > 0:
                has_solution = True
                edge_case = 'no'
                return solution, w, has_solution, edge_case

    # edge cases
    if np.sum(solution) == 0:
        if dist_from_top(av_goal_df, average)<= set_size:
            isTop = True
            isOther = False
            edge_case = "top"
        elif dist_from_bottom(av_goal_df, average) <= set_size:
            isTop = False
            isOther = False
            edge_case = 'bottom'
        else:
            isTop = False
            isOther = False
            edge_case = 'other'
        solution = get_special_set(av_goal_df, average, isTop, isOther, set_size)
        has_solution = True
        return  solution, 0, has_solution, edge_case
    has_solution = False
    edge_case = 'error'
    return np.zeros(set_size), w, has_solution, edge_case



def make_comparison_group(user, average):
    """
    Gets the comparison set and other info from the get_set function and turns it into a JSON to be used by the index page.
    Additionally computes the mean and std of the comparison set and how far the student is from that mean.
    :param user: An instance of iki.User
    :param average: the new average grade of that user
    :return: JSOn version of the comparison set, has_comparison, solution_mean, solution_std, solution_mean_distance,
    edge_case.
    """
    # alternatively, get the goal grade from the "body" attribute from the submission for an assignment in which we ask
    # for the goal grade. And couple that with the current_score function to get the average-goal tuple

    goal = user.goal_grade
    # average = user.av_grade


    av_goal_df = get_av_goal_data(user)
    solution, window, has_comparison, edge_case = get_set(average, goal, av_goal_df, 7)
    print('solution')
    print(solution)
    group_as_frequency = frequency_count_comp(solution, average)
    solution_mean = np.mean(solution)
    solution_std = np.std(solution)
    solution_mean_distance = abs(average-solution_mean)
    return group_as_frequency, has_comparison, solution_mean, solution_std, solution_mean_distance, edge_case



############# This part is not used

def set_goal_grade(goal, student_id):
    user = User.objects.filter(iki_user_id=student_id)[0]
    user.goal_grade = float(goal)
    comparison_group, has_comparison = make_set_for_diagram(user)
    user.has_comparison_group = has_comparison
    user.comparison_group = json.dumps(comparison_group)
    user.save()
    # make_comparison_group(user)


def make_set_for_diagram(user):
    """
    Generates the data that will be included in the social comparison diagram for a user. That data consists of a
    defined number of peers students such that the mean current grade of that selection is higher than the current grade
    of the user by +0.5 to +1.0
    :param user: the user for which the data must be generated
    :return: a JSON consisting of the peer students selected for the comparison diagram.
    """
    # in this variable will be stored the solution of the subset sum problem
    solution = []


    def average_subset_algorithm(arr: pd.DataFrame, n, v, sum, set_size, l_b, u_b):
        """
        This function finds a comparison set, such that the size of the set is defined by a constraint and the mean of
        set lies within a defined boundary. This algorithm is a variant the subset mean problem, to which was added a
        size constraint upper and lower bounds instead of a mean. This algorithm relies on the fact that the means of a
        set equals the mean of the values of the set divided by its size. Therefore by defining the desired size of our
        subset, we can search for a subset which mean = mean * set size.
        :param arr: the array from to find the subset
        :param n: the size of arr.
        :param v: an array that will be filled with the members of the solution. Only used in the recursion. Do not set
        a value when calling the function
        :param sum: the desired mean of the members of the set times the desired size of the set
        :param set_size: the desired size of the set
        :param l_b: upper bound
        :param u_b: lower bound
        :param solution: the subset found for the given constraint with the largest mean.
        """

        # if the mean of the subset falls into the desired range, add the subset to the list of solutions
        if (l_b*set_size <=sum <= u_b*set_size and len(v)==set_size):
            if solution and np.mean(solution[-1]) < np.mean(v):
                solution.append(v)
                return

        # If no remaining elements,
        if (n == 0):
            return

        # We consider two cases for every element.
        # a) We do not include last element.
        # b) We include last element in current subset.
        average_subset_algorithm(arr, n - 1, v, sum, set_size, l_b, u_b)
        v1 = [] + v
        v1.append(arr[n - 1])
        average_subset_algorithm(arr, n - 1, v1, sum - arr[n - 1], set_size, l_b, u_b)


    goal_grade = user.goal_grade
    average = user.av_grade + 1

    av_goal_df = get_av_goal_data(user)

    # The maximum size of the peer group with similar goals. The reason for setting a maximum size is to upper-bound the
    # computational load of the comparison set making algorithm (which runs in O(2^n)
    size = 20
    peers, w = get_same_goal_set(av_goal_df, goal_grade, size)
    set_size = 7
    lower_bound = (average+0.5)*set_size
    upper_bound = (average+0.5)*set_size

    # the desired size of the comparison set

    v= []
    average_subset_algorithm(peers, len(peers), v, average*set_size, set_size, lower_bound, upper_bound)
    has_comparison = solution != []

    return frequency_count_comp(solution, average), has_comparison
