# from django.db import models
# from django_app_lti.models import LTICourse, LTICourseUser, LTIResource
# from django.contrib.auth.models import AbstractUser
#
#
# # Create your models here.
# class MyLTICourse(LTICourse):
#     """Add attribute: canvas_course_id
#     """
#     canvas_course_id = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return "%s (ID: %s)" % (self.course_name, self.id)
#
#
# class User(AbstractUser):
#     """User.
#
#     User is an entity in the database with the following features:
#     - full_name: full name of the user
#     - email: email of the user.
#     - verified_email: Boolean to indicate if the user has validated their email address.
#     - USERNAME_FIELD: username of the username.
#     - password: the hash of the password of the user.
#     - lti_id: the DLO id of the user.
#     """
#
#     #course = models.ForeignKey(MyLTICourse, on_delete=models.PROTECT)
#
#     full_name = models.CharField(
#         null=False,
#         max_length=200
#     )
#     email = models.EmailField(
#         unique=True,
#     )
#     verified_email = models.BooleanField(
#         default=False
#     )
#     lti_id = models.TextField(
#         null=True,
#         unique=True,
#         blank=True,
#     )
#     profile_picture = models.TextField(
#         null=True
#     )
#     #is_teacher = models.BooleanField(default=False)
#
#     role = models.CharField(max_length=2048, blank=True, null=True, verbose_name="Roles")
#
#     # @classmethod
#     # def hasCourseUser(cls, lti_id, course):
#     #     return cls.objects.filter(lti_id=lti_id, course=course).exists()
#     #
#     # @classmethod
#     # def getCourseUser(cls, lti_id, course):
#     #     result = cls.objects.filter(lti_id=lti_id, course=course)
#     #     if len(result) > 0:
#     #         return result[0]
#     #     return None
#     #
#     # def updateRoles(self, roles):
#     #     if self.roles != roles:
#     #         self.roles = roles
#     #         self.save()
#     #         return True
#     #     return False
#
#     @classmethod
#     def createCourseUser(course, lti_id, email=None, profile_picture=None,
#               is_superuser=False, is_teacher=False, full_name=None):
#         """Create a user.
#
#         Arguments:
#         username -- username (is the user came from the UvA canvas, this will be its studentID)
#         password -- password of the user to login
#         email -- mail of the user (default: none)
#         lti_id -- to link the user to canvas (default: none)
#         profile_picture -- profile picture of the user (default: none)
#         is_superuser -- if the user needs all permissions, set this true (default: False)
#         """
#         user = User(email=email, lti_id=lti_id, is_superuser=is_superuser,
#                     is_teacher=is_teacher)
#
#         user.full_name = full_name
#
#         user.save()
#         # user.set_password(password)
#         # if profile_picture:
#         #     user.profile_picture = profile_picture
#         # else:
#         #     user.profile_picture = '/static/unknown-profile.png'
#         # user.save()
#         return user
#
#
# class Course(models.Model):
#     """Course.
#
#     A Course entity has the following features:
#     - name: name of the course.
#     - author: the creator of the course.
#     - abbreviation: a max three letter abbreviation of the course name.
#     - startdate: the date that the course starts.
#     - lti_ids: the ids of the course linked over LTI.
#     """
#
#     name = models.TextField()
#     abbreviation = models.TextField(
#         max_length=10,
#         default='XXXX',
#     )
#
#     author = models.ForeignKey(
#         'User',
#         on_delete=models.SET_NULL,
#         null=True
#     )
#
#     users = models.ManyToManyField(
#         'User',
#         related_name='participations',
#         through='Participation',
#         through_fields=('course', 'user'),
#     )
#
#     startdate = models.DateField(
#         null=True,
#     )
#     enddate = models.DateField(
#         null=True,
#     )
#
#     def to_string(self, user=None):
#         if user is None:
#             return "Course"
#         if not user.can_view(self):
#             return "Course"
#
#         return self.name + " (" + str(self.pk) + ")"
#
#
# class Group(models.Model):
#     """Group.
#
#     A Group entity has the following features:
#     - name: the name of the group
#     - course: the course where the group belongs to
#     """
#     name = models.TextField()
#
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE
#     )
#
#     lti_id = models.TextField(
#         null=True,
#         unique=False,
#     )
#
#     class Meta:
#         """Meta data for the model: unique_together."""
#         unique_together = ('name', 'course')
#
#     def to_string(self, user=None):
#         if user is None:
#             return "Group"
#         if not user.can_view(self.course):
#             return "Group"
#         return "{} ({})".format(self.name, self.pk)
#
#
# class Role(models.Model):
#     """Role.
#
#     A complete overview of the role requirements can be found here:
#     https://docs.google.com/spreadsheets/d/1M7KnEKL3cG9PMWfQi9HIpRJ5xUMou4Y2plnRgke--Tk
#
#     A role defines the permissions of a user group within a course.
#     - name: name of the role
#     - list of permissions (can_...)
#     """
#     name = models.TextField()
#
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE
#     )
#
#     can_edit_course_details = models.BooleanField(default=False)
#     can_delete_course = models.BooleanField(default=False)
#     can_edit_course_roles = models.BooleanField(default=False)
#     can_view_course_users = models.BooleanField(default=False)
#     can_add_course_users = models.BooleanField(default=False)
#     can_delete_course_users = models.BooleanField(default=False)
#     can_add_course_user_group = models.BooleanField(default=False)
#     can_delete_course_user_group = models.BooleanField(default=False)
#     can_edit_course_user_group = models.BooleanField(default=False)
#     can_add_assignment = models.BooleanField(default=False)
#     can_delete_assignment = models.BooleanField(default=False)
#
#     can_edit_assignment = models.BooleanField(default=False)
#     can_view_all_journals = models.BooleanField(default=False)
#     can_grade = models.BooleanField(default=False)
#     can_publish_grades = models.BooleanField(default=False)
#     can_have_journal = models.BooleanField(default=False)
#     can_comment = models.BooleanField(default=False)
#     can_view_unpublished_assignment = models.BooleanField(default=False)
#
#     def save(self, *args, **kwargs):
#         if self.can_add_course_users and not self.can_view_course_users:
#             raise ValidationError('A user needs to view course users in order to add them.')
#
#         if self.can_delete_course_users and not self.can_view_course_users:
#             raise ValidationError('A user needs to view course users in order to remove them.')
#
#         if self.can_edit_course_user_group and not self.can_view_course_users:
#             raise ValidationError('A user needs to view course users in order to manage user groups.')
#
#         if self.can_view_all_journals and self.can_have_journal:
#             raise ValidationError('An administrative user is not allowed to have a journal in the same course.')
#
#         if self.can_grade and not self.can_view_all_journals:
#             raise ValidationError('A user needs to be able to view journals in order to grade them.')
#
#         if self.can_publish_grades and not (self.can_view_all_journals and self.can_grade):
#             raise ValidationError('A user should not be able to publish grades without being able to view or grade \
#                                   the journals.')
#
#         if self.can_comment and not (self.can_view_all_journals or self.can_have_journal):
#             raise ValidationError('A user requires a journal to comment on.')
#
#         super(Role, self).save(*args, **kwargs)
#
#     def to_string(self, user=None):
#         if user is None:
#             return "Role"
#         if not user.can_view(self.course):
#             return "Role"
#
#         return "{} ({})".format(self.name, self.pk)
#
#     class Meta:
#         """Meta data for the model: unique_together."""
#
#         unique_together = ('name', 'course',)
#
#
# class Participation(models.Model):
#     """Participation.
#
#     A participation defines the way a user interacts within a certain course.
#     The user is now linked to the course, and has a set of permissions
#     associated with its role.
#     """
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     role = models.ForeignKey(
#         Role,
#         on_delete=models.CASCADE,
#         related_name='role',
#     )
#     group = models.ForeignKey(
#         Group,
#         null=True,
#         on_delete=models.SET_NULL,
#         default=None,
#     )
#
#     class Meta:
#         """Meta data for the model: unique_together."""
#
#         unique_together = ('user', 'course',)
#
#     def to_string(self, user=None):
#         if user is None:
#             return "Participation"
#         if not user.can_view(self.course):
#             return "Participation"
#
#         return "user: {}, course: {}, role: {}".format(
#             self.user.to_string(user), self.course.to_string(user), self.role.to_string(user))
#
#
# class Lti_ids(models.Model):
#     """Lti ids
#
#     Contains the lti ids for course and assignments as one course/assignment
#     on our site needs to be able to link to multiple course/assignment in the
#     linked VLE.
#     """
#     #ASSIGNMENT = 'Assignment'
#     COURSE = 'Course'
#     #TYPES = ((ASSIGNMENT, 'Assignment'), (COURSE, 'Course'))
#     #TYPES = (COURSE, 'Course')
#
#     # assignment = models.ForeignKey(
#     #     'Assignment',
#     #     on_delete=models.CASCADE,
#     #     null=True
#     # )
#
#     course = models.ForeignKey(
#         'Course',
#         on_delete=models.CASCADE,
#         null=True
#     )
#
#     lti_id = models.TextField()
#     # for_model = models.TextField(
#     #     choices=TYPES
#     # )
#
#     def to_string(self, user=None):
#         return "Lti_ids"
#
#     # class Meta:
#     #     """A class for meta data.
#     #
#     #     - unique_together: assignment and user must be unique together.
#     #     """
#     #
#     #     unique_together = ('lti_id', 'for_model',)
#
#
# class MyLTICourseUser(LTICourseUser):
#     """Add variable: name
#         changes user value to the value of user_id in the lti POST request
#         Overrides functions to account for these changes
#     """
# #     #name = models.CharField(max_length=2048, blank=True, null=True)
#     user_number = models.CharField(max_length=1024, blank=True, null=True)
#
#     @classmethod
#     def hasCourseUser(cls, user_number, course):
#         return cls.objects.filter(user_number=user_number, course=course).exists()
#
#     @classmethod
#     def getCourseUser(cls, user_number, course):
#         result = cls.objects.filter(user_number=user_number, course=course)
#         if len(result) > 0:
#             return result[0]
#         return None
#
#     @classmethod
#     def createCourseUser(cls, user_number, course, roles=''):
#          course_user = cls.objects.create(user_number=user_number, course=course, roles=roles)
#          return course_user
#
# class MyLTIResource(LTIResource):
#     @classmethod
#     def setupResource(cls, launch, create_course=False):
#         if not ("consumer_key" in launch and "resource_link_id" in launch):
#             raise Exception("Missing required launch parameters: consumer_key and resource_link_id")
#
#         course = None
#         course_name_short = launch.pop('course_name_short', 'untitled')
#         course_name = launch.pop('course_name', 'Untitled Course')
#         canvas_course_id = launch.pop('canvas_course_id', 'untilted')
#         if create_course:
#             course = MyLTICourse.objects.create(course_name_short=course_name_short,course_name=course_name, canvas_course_id=canvas_course_id)
#
#         return cls.objects.create(course=course, **launch)
