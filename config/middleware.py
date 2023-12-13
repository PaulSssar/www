# middleware.py

import base64
from django.http import HttpResponse
from django.conf import settings


class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    username, password = base64.b64decode(auth[1]).decode('utf-8').split(':')
                    if username == settings.BASIC_AUTH_USERNAME and password == settings.BASIC_AUTH_PASSWORD:
                        return self.get_response(request)

        response = HttpResponse("Auth Required", status=401)
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        return response
