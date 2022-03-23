from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_204_NO_CONTENT


class NoContentException(APIException):
    status_code = HTTP_204_NO_CONTENT
    default_code = 'no_content'
    default_detail = 'Requested content no found'
