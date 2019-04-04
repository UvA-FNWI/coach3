from django.db import models

# Create your models here.


class Course(models.Model):
    iki_course_id = models.CharField(max_length=200)
    # startdate = models.DateField(
    #     null=False,
    # )
    # enddate = models.DateField(
    #     null=False,
    # )


class User(models.Model):
    """User.

    User is an entity in the database with the following features:
    - name: full name of the user
    - email: email of the user.
    - lti_id: the DLO id of the user.
    """

    name = models.CharField(null=False, max_length=200)

    email = models.EmailField(unique=True)

    lti_id = models.CharField(null=True, unique=True, blank=True, max_length=200)

    iki_user_id = models.IntegerField(null=True, unique=True, blank=True, max_length=200)


    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    # To Add: average_grade, predicted_average_grade, is_promotion_focused

    def __str__(self):
        return self.name

    def create_user(request):
        """Create a user.

        Arguments:
        name -- full name of the student
        password -- password of the user to login
        email -- mail of the user (default: none)
        lti_id -- to link the user to canvas
        """

        course_id = request['custom_canvas_course_id']
        # @todo: check if user belongs to authorised users by checkin email address against list
        user = User(
            name=request['lis_person_name_full'],
            email=request['lis_person_contact_email_primary'],
            lti_id=request['user_id'],
            iki_user_id=request['custom_canvas_user_id'],
            course=Course.objects.create(iki_course_id=course_id),
            )
        user.save()

        return user

    def get_user_id(self):
        return self.iki_user_id
