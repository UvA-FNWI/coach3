from django.db import models
# from simple_history.models import HistoricalRecords
from utils.ComparisonBuckets import frequency_count_comp
import numpy as np
import json

# Create your models here.


class Course(models.Model):
    """
    Course is an entity in the database representing the course in which the tool is user. It has the following attribute:
    - iki_course_id: the canvas id of the course
    """
    iki_course_id = models.CharField(max_length=200, unique=True)
    # startdate = models.DateField(
    #     null=False,
    # )
    # enddate = models.DateField(
    #     null=False,
    # )


class User(models.Model):
    """
    User is an entity in the database representing the student using the tool, with the following attributes:
    - name: full name of the user
    - email: email of the user.
    - lti_id: the DLO id of the user.
    - iki_user_id: The id of the user for the course
    - course = an entity of Course, representing the course in which the user is using the tool
    - av_grade = the current average grade of the user
    - grade_pred = predicted final grade
    - grade_sigma = standard deviation of the predicted final grade
    - assessments = number of assessments that have been graded so far
    - comparison_group = a JSON containing the number of peers with a certain grade for each grade
    - goal_grade = the goal grade of the user
    - has_comparison_group = Boolean if a comparison group could be made for the user with current average grade and
    goal grade
    - comparison_distance_mean = the distance between the average of the user and the mean grade of the comparison group
    - comparison_mean = the mean grade of the comparison group
    - comparison_std = the standard deviation of the grade distribution of the comparison group
    - edg_case = whether the user falls into an edge case. "top' if in the top 7, "bottom" if in the bottom 7, "other"
    if other, "no" if it does not belong to an edge case, "error" otherwise.
    - log_count = a log of how many time the user has connected to the tool.
    - history = in order to keep a history of the changes
    """

    name = models.CharField(null=False, max_length=200)

    email = models.EmailField(unique=True)

    lti_id = models.CharField(null=True, unique=True, blank=True, max_length=200)

    iki_user_id = models.IntegerField(null=True, unique=True, blank=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    av_grade = models.FloatField(default=0)

    grade_pred = models.FloatField(default=0)

    grade_sigma = models.FloatField(default=0)

    assessments = models.IntegerField(default=0)

    comparison_group = models.TextField(max_length=600)

    goal_grade = models.FloatField(default=0.0)

    has_comparison_group = models.BooleanField(default=False)

    comparison_distance_mean = models.FloatField(default=0.0)

    comparison_mean = models.FloatField(default=0.0)

    comparison_std = models.FloatField(default=0.0)

    edge_case = models.CharField(null=True, max_length=20)

    log_count = models.IntegerField(default=1)

    # history = HistoricalRecords(cascade_delete_history=True)


    def __str__(self):
        return self.name

    def create_user(request):
        """
        Creates a user. Sets a value for the name, email, lti_id, iki_user_id, course, comparison group and goal grade
        :param: a request
        :return: an instance of User
        """

        course_id = request['custom_canvas_course_id']
        object, created = Course.objects.get_or_create(iki_course_id=course_id)
        # @todo: check if user belongs to authorised users by checkin email address against list
        user = User(
            name=request['lis_person_name_full'],
            email=request['lis_person_contact_email_primary'],
            lti_id=request['user_id'],
            iki_user_id=request['custom_canvas_user_id'],
            # course=Course.objects.create(iki_course_id=course_id),
            course = object,
            comparison_group=json.dumps(frequency_count_comp(np.zeros(7), 0)),
            goal_grade = request['goal']
            )
        user.save()

        return user

    def get_user_id(self):
        """
        get the user_id of the user
        :return: iki_user_id
        """
        return self.iki_user_id
