from werkzeug.wsgi import LimitedStream


class StreamConsumingMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        length = 0
        if 'CONTENT_LENGTH' in environ:
            try:
                length = int(environ['CONTENT_LENGTH'])
            except ValueError:
                pass
        stream = LimitedStream(environ['wsgi.input'], length)

        environ['wsgi.input'] = stream
        app_iter = self.app(environ, start_response)
        try:
            stream.exhaust()
            for event in app_iter:
                yield event
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
