from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred"
        if isinstance(response.data, dict) and "detail" in response.data:
            message = str(response.data["detail"])

        response.data = {
            "status_code": response.status_code,
            "success": False,
            "message": message,
            "errors": response.data,
        }

    return response
