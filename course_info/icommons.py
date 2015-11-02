import drest
import json
import logging

from django.core.cache import cache
from canvas_course_info.settings import aws as settings

log = logging.getLogger(__name__)

CACHE_KEY_COURSE_BY_CANVAS_COURSE_ID = 'course-by-canvas-course-id-{}'
CACHE_KEY_COURSE_BY_COURSE_INSTANCE_ID = 'course-by-course-instance-id-{}'
CACHE_KEY_SCHOOL_BY_SCHOOL_ID = 'school-by-school-id-{}'


class ICommonsApi(drest.API):
    @classmethod
    def from_request(cls, request):
        icommons_base_url = settings.ICOMMONS_BASE_URL
        access_token = settings.ICOMMONS_API_TOKEN
        return cls(icommons_base_url, access_token)

    def __init__(self, icommons_base_url, access_token):
        self.headers = {'Authorization': "Token %s" % access_token,
                        'Content-Type': 'application/json'}
        api_path = settings.ICOMMONS_API_PATH
        super(ICommonsApi, self).__init__(icommons_base_url + api_path,
                                          extra_headers=self.headers,
                                          timeout=60,
                                          serialize=True,
                                          trailing_slash=False)

    def get_course_info(self, course_instance_id):
        cache_key = CACHE_KEY_COURSE_BY_COURSE_INSTANCE_ID.format(course_instance_id)
        course_info = cache.get(cache_key)
        if course_info is None:
            course_info = {}
            # get the course_instance data
            try:
                relative_url = '/course_instances/%s/?format=json' % course_instance_id
                response = self.make_request('GET', relative_url,
                                             headers=self.headers)
                course_info = response.data
                log_msg = "Caching course info for course_instance_id {}: {}"
                log.debug(log_msg.format(course_instance_id, json.dumps(course_info)))
                cache.set(cache_key, course_info)
            except Exception as e:
                log.exception(e.message)
        return course_info

    def get_course_info_by_canvas_course_id(self, canvas_course_id):
        cache_key = CACHE_KEY_COURSE_BY_CANVAS_COURSE_ID.format(canvas_course_id)
        course_info = cache.get(cache_key)
        if course_info is None:
            course_info = {}
            # get the course_instance data
            try:
                relative_url = '/course_instances/?format=json&canvas_course_id=%s' % canvas_course_id
                response = self.make_request('GET', relative_url,
                                             headers=self.headers)
                results = response.data.get('results', [])
                if len(results):
                    primary_cid = self._get_primary_course_instance_id(results)
                    if primary_cid:
                        course_info = self.get_course_info(primary_cid)
                log_msg = "Caching course info for canvas_course_id {}: {}"
                log.debug(log_msg.format(canvas_course_id, json.dumps(course_info)))
                cache.set(cache_key, course_info)
            except Exception as e:
                log.exception(e.message)
        return course_info

    def get_school_info(self, school_id):
        """
            retrieves - from the iCommons API - the information
            about the school passed in (by its school id),
            or logs an error and returns an empty dict if there is no such school
        """
        cache_key = CACHE_KEY_SCHOOL_BY_SCHOOL_ID.format(school_id)
        school_info = cache.get(cache_key)
        if school_info is None:
            school_info = {}
            try:
                relative_url = '/schools/%s/?format=json' % school_id
                response = self.make_request('GET', relative_url,
                                             headers=self.headers)
                school_info = response.data
                log_msg = "Caching school info for school_id {}: {}"
                log.debug(log_msg.format(school_id, json.dumps(school_info)))
                cache.set(cache_key, school_info)
            except Exception as e:
                log.error(e.message)
        return school_info
        # This function could be made to return only the school name or an error, as that's the only thing we need it
        # for right now (in views.py, to insert the school name before the display number).
        # But just in case we want to use it for more than that in the future, and so that it mirrors 'get_course_info,'
        # we're going to let it return the whole data set.

    def _get_primary_course_instance_id(self, course_instances):
        primary_cids = [c['course_instance_id'] for c in course_instances if not c['primary_xlist_instances']]
        if len(primary_cids) == 1:
            return primary_cids[0]
        elif len(primary_cids) == 0:
            error_msg = 'No primary course instance found'
        else:
            error_msg = 'Multiple possible primary courses found, cannot determine primary'
        log.error('{}: {}'.format(error_msg, course_instances))
        return None
