import json
import logging


class Code200LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('code200')

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        try:
            content = response.content.decode()
            content = json.loads(response.content.decode())
        # except Exception:
        except json.JSONDecodeError:
            content = {}
        # if '200' in content:
        if content.get('code') == 200:
            self.logger.info('Status code 200 in:%s' % {request.path})
        return response
