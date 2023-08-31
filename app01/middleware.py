import json
import logging


class CodeNot200LoggingMiddleware:
    """
        tag10，创建中间件
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('code_not200')

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        try:
            content = json.loads(response.content.decode())
        except json.JSONDecodeError:
            content = {}
        if content.get('code') != 200:
            self.logger.info('Status code not 200:%s' % {request.path})
        return response
