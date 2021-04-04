from rest_framework.exceptions import APIException


class Conflict(APIException):
    default_code = 409
