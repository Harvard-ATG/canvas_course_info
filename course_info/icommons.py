import json
import logging
import urlparse

import requests
from django.core.cache import cache
from canvas_course_info.settings import aws as settings


logger = logging.getLogger(__name__)

CACHE_KEY_COURSE_BY_CANVAS_COURSE_ID = 'course-by-canvas-course-id-{}'
CACHE_KEY_COURSE_BY_COURSE_INSTANCE_ID = 'course-by-course-instance-id-{}'
CACHE_KEY_SCHOOL_BY_SCHOOL_ID = 'school-by-school-id-{}'


class ICommonsApi(object):
    def __init__(self, icommons_base_url=None, access_token=None):
        if not icommons_base_url:
            icommons_base_url = settings.ICOMMONS_BASE_URL
        if not access_token:
            access_token = settings.ICOMMONS_API_TOKEN
        api_path = settings.ICOMMONS_API_PATH

        self.base_url = '/'.join((icommons_base_url.rstrip('/'),
                                  api_path.strip('/'))) + '/'
        self.session = requests.Session()
        self.session.headers = {'Authorization': 'Token %s' % access_token}
        self.session.params = {'format': 'json'}

    def _get_objects(self, type_, id_, **kwargs):
        path = '{}/'.format(type_)
        if id_:
            path += '{}/'.format(id_)
        url = urlparse.urljoin(self.base_url, path)
        response = self.session.get(url, params=kwargs)
        try:
            response.raise_for_status()
        except Exception as e:
            logger.exception(u'Error getting {}: {}'.format(url, response.text))
            raise
        return response.json()

    def _get_course_instances(self, course_instance_id=None, **kwargs):
        return self._get_objects('course_instances', course_instance_id, **kwargs)

    def _get_schools(self, school_id=None, **kwargs):
        return self._get_objects('schools', school_id, **kwargs)

    def get_course_info(self, course_instance_id):
        cache_key = CACHE_KEY_COURSE_BY_COURSE_INSTANCE_ID.format(course_instance_id)
        course_info = cache.get(cache_key)
        if course_info is None:
            course_info = {}
            # get the course_instance data
            try:
                course_info = self._get_course_instances(course_instance_id)
                log_msg = u'Caching course info for course_instance_id {}: {}'
                logger.debug(log_msg.format(course_instance_id, json.dumps(course_info)))
                cache.set(cache_key, course_info)
            except Exception as e:
                logger.exception(e.message)
        return course_info

    def get_course_info_by_canvas_course_id(self, canvas_course_id):
        cache_key = CACHE_KEY_COURSE_BY_CANVAS_COURSE_ID.format(canvas_course_id)
        course_info = cache.get(cache_key)
        if course_info is None:
            course_info = {}
            # get the course_instance data
            try:
                course_instances = self._get_course_instances(
                                       canvas_course_id=canvas_course_id)['results']
                if len(course_instances):
                    course_instance_id = self._get_course_instance_id(course_instances)
                    if course_instance_id:
                        course_info = self.get_course_info(course_instance_id)
                log_msg = u'Caching course info for canvas_course_id {}: {}'
                logger.debug(log_msg.format(canvas_course_id, json.dumps(course_info)))
                cache.set(cache_key, course_info)
            except Exception as e:
                logger.exception(e.message)
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
                school_info = self._get_schools(school_id = school_id)
                log_msg = u'Caching school info for school_id {}: {}'
                logger.debug(log_msg.format(school_id, json.dumps(school_info)))
                cache.set(cache_key, school_info)
            except Exception as e:
                logger.error(e.message)
        return school_info
        # This function could be made to return only the school name or an error, as that's the only thing we need it
        # for right now (in views.py, to insert the school name before the display number).
        # But just in case we want to use it for more than that in the future, and so that it mirrors 'get_course_info,'
        # we're going to let it return the whole data set.

    def _get_course_instance_id(self, course_instances):
        if not course_instances:
            return None
        if len(course_instances) == 1:
            # Only one course found with the requested canvas course id;
            # we'll use its course instance ID for the course info lookup
            return course_instances[0]['course_instance_id']

        # we have multiple courses with the requested canvas course id, use
        # the primary to look up the course information
        primary_cids = [c['course_instance_id'] for c in course_instances if not c['primary_xlist_instances']]
        if len(primary_cids) == 1:
            return primary_cids[0]
        elif len(primary_cids) == 0:
            error_msg = 'No primary course instance found'
        else:
            error_msg = 'Multiple possible primary courses found, cannot determine primary'
        logger.error(u'{}: {}'.format(error_msg, course_instances))
        return None
