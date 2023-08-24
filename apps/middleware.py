from django.http import HttpResponse

from apps.utils import get_logger

"""
def timing(get_response):
    def middleware(request: Request):
        response = get_response(request)
        print(request.user)
        print(request.method)
        return response

    return middleware

 """


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger = get_logger()
            logger.exception(e)

    def process_template_response(self, request, response):
        # print("process_template_response")
        return response

    def process_exception(self, request, exception):
        return HttpResponse(exception)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # print("process_view")
        ...
