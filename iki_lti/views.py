from django_app_lti.views import LTILaunchView
from .models import MyLTIResource, MyLTICourseUser, MyLTIResource
#from django_app_lti.models import LTICourseUser
#from django.http import HttpResponse
#from django.template import Context, loader
#from django.shortcuts import render, redirect
#from utils.CanvasHelper import get_data, given_consent
#import json


from django.conf import settings
#from django.core.urlresolvers import reverse

LTI_SETUP = settings.LTI_SETUP
INITIALIZE_MODELS = LTI_SETUP.get('INITIALIZE_MODELS', False)


class MyLTILaunchView(LTILaunchView):
    def initialize_models(self, request):
        '''
        Helper function to process the post request and setup models.
        '''

        # Collect a subset of the LTI launch parameters for mapping the
        # tool resource instance to this app's internal course instance.
        launch = {
            "consumer_key": request.POST.get('oauth_consumer_key', None),
            "resource_link_id": request.POST.get('resource_link_id', None),
            "context_id": request.POST.get('context_id', None),
            "course_name_short": request.POST.get("context_label"),
            "course_name": request.POST.get("context_title"),
            "canvas_course_id": request.POST.get('custom_canvas_course_id', None),
            #"user": request.POST.get('user_id', None),
        }

        # Lookup tool resource, uniquely identified by the combination of:
        #
        #  * oauth consumer key
        #  * resource link ID
        #
        # These are required attributes specified by LTI (context ID is not).
        # If no LTI resource is found, automatically setup a new course instance
        # and associate it with the LTI resource.
        resource_identifiers = [launch[x] for x in ('consumer_key', 'resource_link_id')]
        print("1")
        if MyLTIResource.hasResource(*resource_identifiers):
            print("2")
            lti_resource = MyLTIResource.getResource(*resource_identifiers)
        else:
            create_course = INITIALIZE_MODELS in ("resource_and_course", "resource_and_course_users")
            lti_resource = MyLTIResource.setupResource(launch, create_course)
            if lti_resource.course:
                request.session['course_id'] = lti_resource.course.id

        # Associate the authenticated user with the course instance.
        if INITIALIZE_MODELS == "resource_and_course_users":
            launch_roles = request.POST.get('roles', '')
            user=request.POST.get('user_id', None)
            if MyLTICourseUser.hasCourseUser(user_number=user, course=lti_resource.course):
                lti_course_user = MyLTICourseUser.getCourseUser(user_number=user, course=lti_resource.course)
                lti_course_user.updateRoles(launch_roles)
            else:
                lti_course_user = MyLTICourseUser.createCourseUser(user_number=user, course=lti_resource.course, roles=launch_roles)

        # save a reference to the LTI resource object
        self.lti_resource = lti_resource

        return self
