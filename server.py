import json
import re
import http.client

'''framework'''


class App:
    def __init__(self):
        self.handlers = {}

    def get_handler(self, environ):
        current_method = environ['REQUEST_METHOD']
        url = environ['PATH_INFO']
        current_url_handler, allowed_methods, url_params = None, None, None
        for url_regexp, (handler, methods) in self.handlers.items():
            url_match = re.match(url_regexp, url)
            if url_match is None:
                continue
            url_params = url_match.groupdict()
            current_url_handler = handler
            allowed_methods = methods
            break
        if current_url_handler is None:
            current_url_handler = self.not_found_handler
            allowed_methods = ['GET']

        if current_method not in allowed_methods:
            current_url_handler = self.not_allowed_handler
        return current_url_handler, url_params

    def __call__(self, environ, start_response):
        url_params = None
        current_url_handler, url_params = self.get_handler(environ)
        response_text, status_code, extra_headers = current_url_handler(
            environ,
            url_params)

        status_code_message = '%s %s' % (
            status_code,
            http.client.responses[status_code]
        )
        headers = {
            'Content-Type': 'text/plain',
        }
        headers.update(extra_headers)

        if isinstance(response_text, (list, dict)):
            response_text = json.dumps(response_text)
            headers['Content-Type'] = 'text/json'
        start_response(status_code_message,
                       list(headers.items())
                       )
        return [response_text.encode()]

    def register_handler(self, url, methods=None):
        methods = methods or ['GET']

        def wrapped(handler):
            self.handlers[url] = handler, methods
        return wrapped

    @staticmethod
    def not_found_handler(environ, url_params):
        return 'Not found', 404, {}

    @staticmethod
    def not_allowed_handler(environ, url_params):
        return 'Not allowed', 405, {}


'''usage: demo site'''
application = App()


@application.register_handler('^/')
def index_url_handler(environ, url_params):
    return 'Index Page', 200, {}


@application.register_handler('^/cart/', methods=['GET', 'POST'])
def cart_url_handler(environ, url_params):
    return 'Cart Page', 200, {}


@application.register_handler('^/products/')
def info_url_handler(environ, url_params):
    data = [
        {'title': 'Iphone X', 'price': '5000'},
        {'title': 'Iphone 8', 'price': '4000'}
    ]
    return data, 201, {'X-test': '123'}


# @application.register_handler('/products/123/')
@application.register_handler('^/products/(?P<product_id>\d+)/$')
def product_url_handler(environ, url_params):
    data = {'title': 'Iphone 8', 'price': '4000', 'params': url_params}
    return data, 201, {'X-test': '123'}
