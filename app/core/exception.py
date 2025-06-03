from django.core.exceptions import NON_FIELD_ERRORS
from rest_framework.views import exception_handler


def _get_exception_body(status, message):
    return {"status": status, "payload": {"message": message}}


def get(exception, message=None, status="fail"):
    body = _get_exception_body(status, message)
    return exception(body)


def _get_list_error(message):
    return [{NON_FIELD_ERRORS: [message]}]


def get_list_error(exception, message=None):
    return exception(_get_list_error(message))


def exception_handler_override(exc, context):
    """
    Standartized exception handler. Returns django validation errors in format {"detail": value}
    :param exc:
    :param context:
    :return:
    """

    def obj_to_detail(data, field_name=None):
        if isinstance(data, list):
            items = [one for one in data if one]
            data = next(iter(items), None)
            return obj_to_detail(data, field_name=field_name)
        elif isinstance(data, dict):
            items = [one for one in data.items() if one]
            field_name, data = next(iter(items), {None, None})
            return obj_to_detail(data, field_name=field_name)
        else:
            return str(data), field_name

    response = exception_handler(exc, context)

    if response is None:
        return response

    if "detail" not in response.data:
        print(response.data)
        detail, field_name = obj_to_detail(response.data)

        if field_name:
            field_name_capital = field_name.replace("_", " ").capitalize()
            detail = detail.replace("This field", field_name_capital).replace(
                "this value", field_name
            )

        response.data = {"detail": detail}

    return response
