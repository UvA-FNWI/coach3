from django.db import models
from django_app_lti.models import LTICourse, LTICourseUser, LTIResource


# Create your models here.
class MyLTICourse(LTICourse):
    """Add attribute: canvas_course_id
    """
    canvas_course_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "%s (ID: %s)" % (self.course_name, self.id)


class MyLTICourseUser(LTICourseUser):
    """Add variable: name
        changes user value to the value of user_id in the lti POST request
        Overrides functions to account for these changes
    """
#     #name = models.CharField(max_length=2048, blank=True, null=True)
    user_number = models.CharField(max_length=1024, blank=True, null=True)

    @classmethod
    def hasCourseUser(cls, user_number, course):
        return cls.objects.filter(user_number=user_number, course=course).exists()

    @classmethod
    def getCourseUser(cls, user_number, course):
        result = cls.objects.filter(user_number=user_number, course=course)
        if len(result) > 0:
            return result[0]
        return None

    @classmethod
    def createCourseUser(cls, user_number, course, roles=''):
         course_user = cls.objects.create(user_number=user_number, course=course, roles=roles)
         return course_user

class MyLTIResource(LTIResource):
    @classmethod
    def setupResource(cls, launch, create_course=False):
        if not ("consumer_key" in launch and "resource_link_id" in launch):
            raise Exception("Missing required launch parameters: consumer_key and resource_link_id")

        course = None
        course_name_short = launch.pop('course_name_short', 'untitled')
        course_name = launch.pop('course_name', 'Untitled Course')
        canvas_course_id = launch.pop('canvas_course_id', 'untilted')
        if create_course:
            course = MyLTICourse.objects.create(course_name_short=course_name_short,course_name=course_name, canvas_course_id=canvas_course_id)

        return cls.objects.create(course=course, **launch)
