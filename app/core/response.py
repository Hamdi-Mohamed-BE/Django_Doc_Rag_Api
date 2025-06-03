from rest_framework.response import Response
from rest_framework import status as http_status


def _get_response_body(status, payload):
    return {"status": status, "payload": payload}


def internal_error(payload=None):
    body = _get_response_body("fail", payload)
    status = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(body, status)


def not_found(payload=None):
    body = _get_response_body("fail", payload)
    status = http_status.HTTP_404_NOT_FOUND
    return Response(body, status)


def forbidden(payload=None):
    body = _get_response_body("fail", payload)
    status = http_status.HTTP_403_FORBIDDEN
    return Response(body, status)


def unauthorized(payload=None):
    body = _get_response_body("fail", payload)
    status = http_status.HTTP_401_UNAUTHORIZED
    return Response(body, status)


def bad_request(payload=None):
    body = _get_response_body("fail", payload)
    status = http_status.HTTP_400_BAD_REQUEST
    return Response(body, status)


def accepted(payload=None):
    body = _get_response_body("success", payload)
    status = http_status.HTTP_202_ACCEPTED
    return Response(body, status)


def created(payload=None):
    body = _get_response_body("success", payload)
    status = http_status.HTTP_201_CREATED
    return Response(body, status)


def ok(payload=None):
    body = _get_response_body("success", payload)
    status = http_status.HTTP_200_OK
    return Response(body, status)
