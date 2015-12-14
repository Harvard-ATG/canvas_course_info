import json
import logging
import re
import urlparse

import requests
from django.core.cache import cache
from canvas_course_info.settings import aws as settings
from voluptuous import All, Invalid, Range, Required, Schema, ALLOW_EXTRA


logger = logging.getLogger(__name__)

CACHE_KEY_COURSE_BY_CANVAS_COURSE_ID = 'course-by-canvas-course-id-{}'
CACHE_KEY_COURSE_BY_COURSE_INSTANCE_ID = 'course-by-course-instance-id-{}'
CACHE_KEY_SCHOOL_BY_SCHOOL_ID = 'school-by-school-id-{}'
CACHE_KEY_COURSE_PEOPLE_BY_COURSE_INSTANCE_ID = 'course-people-by-canvas-course-id-{}'
# ROLE_IDS translate following  roles-  1 : "Course Head", 2 : "Faculty"
INSTRUCTOR_ROLE_IDS = [1, 2]


# this isn't a full description of the resources, just what we're going to
# expect to be in them within this library
def url(value):
    return bool(re.search('^https?://', value))

course_instance_schema = Schema({
    Required('course_instance_id'): All(int, Range(min=1)),
}, extra=ALLOW_EXTRA)

school_schema = Schema({
    Required('title_long'): basestring,
}, extra=ALLOW_EXTRA)

course_person_schema = Schema({
    Required('user_id'): basestring,
}, extra=ALLOW_EXTRA)


class ICommonsApiValidationError(RuntimeError):
    pass


class ICommonsApi(object):
    def __init__(self, icommons_base_url=settings.ICOMMONS_BASE_URL,
                 access_token=settings.ICOMMONS_API_TOKEN):
        api_path = settings.ICOMMONS_API_PATH

        # we want to keep the full base url and append the api_path.  to get
        # urljoin to do that, we need to ensure the base url has a trailing /,
        # and that the path doesn't have a leading /.
        self.base_url = urlparse.urljoin(icommons_base_url.rstrip('/') + '/',
                                         api_path.lstrip('/'))
        self.session = requests.Session()
        self.session.headers = {'Authorization': 'Token %s' % access_token}
        self.session.params = {'format': 'json'}

    def _get_resource_by_url(self, url, **kwargs):
        # Since session.get doesn't grab the value of 'verify' if it is passed as a kwarg, need to pass it in explicitly
        verify_value = not settings.ICOMMONS_REST_API_SKIP_CERT_VERIFICATION
        response = self.session.get(url, params=kwargs, verify=verify_value)
        try:
            response.raise_for_status()
        except Exception:
            logger.exception(u'Error getting {}: {}'.format(url, response.text))
            raise
        return response.json()

    def _get_resource(self, type_, id_,sub_resource_=None, **kwargs):
        path = '{}/'.format(type_)
        if id_:
            path += '{}/'.format(id_)

        # check for sub_resource_ and append it to the resource url
        if sub_resource_:
            path += '{}/'.format(sub_resource_)

        url = urlparse.urljoin(self.base_url, path)
        return self._get_resource_by_url(url, **kwargs)

    def _get_course_instances(self, course_instance_id=None, **kwargs):
        rv = self._get_resource('course_instances', course_instance_id, **kwargs)
        try:
            if 'results' in rv:
                for instance in rv['results']:
                    course_instance_schema(instance)
            else:
                course_instance_schema(rv)
        except Invalid as e:
            logger.exception(
                u'Unable to validate course instance(s) %s returned from '
                u'the icommons api.', rv)
            raise ICommonsApiValidationError(str(e))
        return rv

    def _get_schools(self, school_id=None, **kwargs):
        rv = self._get_resource('schools', school_id, **kwargs)
        try:
            if 'results' in rv:
                for instance in rv['results']:
                    school_schema(instance)
            else:
                school_schema(rv)
        except Invalid as e:
            logger.exception(
                u'Unable to validate school(s) %s returned from the icommons '
                u'api.', rv)
            raise ICommonsApiValidationError(str(e))
        return rv

    def _course_info_instructor_list(self, course_instance_id, **kwargs):

        # We need to fetch sub resource 'people'. Send that as a param to append  to the resource url
        #  to get course people data
        sub_resource = 'people'

        instructors = None
        rv = self._get_resource('course_instances', course_instance_id, sub_resource, **kwargs)
        try:
            if 'results' in rv:
                instructors = []
                for person in rv['results']:
                    course_person_schema(person)
                    if person.get('role') and person.get('role')['role_id'] in INSTRUCTOR_ROLE_IDS:
                        instructors.append(person)

        except Invalid as e:
            logger.exception(
                u'Unable to validate course instance(s) %s returned from '
                u'the icommons api.', rv)
            raise ICommonsApiValidationError(str(e))
        return instructors

    def _parse_type_and_id_from_url(self, url):
        return url.replace(self.base_url, '').split('/')[:2]

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
            except Exception:
                logger.exception('Error retrieving course instance by id %s',
                                 course_instance_id)
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
                school_info = self._get_schools(school_id=school_id)
                log_msg = u'Caching school info for school_id {}: {}'
                logger.debug(log_msg.format(school_id, json.dumps(school_info)))
                cache.set(cache_key, school_info)
            except Exception as e:
                logger.error(e.message)
        return school_info

    def get_course_info_instructor_list(self, course_instance_id=None):
        """
            retrieves course instructors information from the iCommons API
            or returns None if there are no instructors
        """
        cache_key = CACHE_KEY_COURSE_PEOPLE_BY_COURSE_INSTANCE_ID.format(course_instance_id)
        course_staff_info = cache.get(cache_key)
        if course_staff_info is None:
            try:
                course_staff_info = self._course_info_instructor_list(course_instance_id=course_instance_id)
                log_msg = u'Caching course info people for course_instance_id {}: {}'
                logger.debug(log_msg.format(course_instance_id, json.dumps(course_staff_info)))
                cache.set(cache_key, course_staff_info)
            except Exception as e:
                logger.error(e.message)
        return course_staff_info

    def _get_course_instance_id(self, course_instances):
        if not course_instances:
            return None

        if len(course_instances) == 1:
            course_instance = course_instances[0]
            if course_instance.get('primary_xlist_instances'):
                logger.debug(
                    u'iCommons api returned a single, secondary instance for '
                    u'canvas course id %s', course_instance['course_instance_id'])
                primary_urls = course_instance['primary_xlist_instances']
                # it should never be the case that there are multiple primaries
                # for a secondary
                if len(primary_urls) > 1:
                    logger.warning(
                        u'iCommons api returned multiple primary instances %s '
                        u'for course instance %s',
                        primary_urls, course_instance)
                    return None
                course_instance = self._get_resource_by_url(primary_urls[0])
            return course_instance['course_instance_id']

        # we have multiple courses with the requested canvas course id, let's
        # see if they agree on which one is primary
        primary_cids = set()
        for ci in course_instances:
            if ci.get('primary_xlist_instances'):
                if len(ci['primary_xlist_instances']) > 1:
                    logger.warning(
                        u'iCommons api returned multiple primary instances %s '
                        u'for course instance %s',
                        ci['primary_xlist_instances'], ci)
                    return None
                _, id_ = self._parse_type_and_id_from_url(
                             ci['primary_xlist_instances'][0])
                primary_cids.add(id_)  # unicode string
            else:
                # must also be unicode string to match any dupes found above
                primary_cids.add(u'{}'.format(ci['course_instance_id']))
        if len(primary_cids) == 1:
            return primary_cids.pop()
        elif len(primary_cids) == 0:
            error_msg = 'No primary course instance found'
        else:
            error_msg = 'Multiple possible primary courses found, cannot determine primary'
        logger.error(u'{}: {}'.format(error_msg, course_instances))
        return None
