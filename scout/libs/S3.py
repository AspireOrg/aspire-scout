import boto3


class S3(object):
    app = None
    s3 = None
    s3c = None
    bucket = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.bucket = app.config['S3_BUCKET']
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=app.config['S3_KEY'],
            aws_secret_access_key=app.config['S3_SECRET']
        )
        self.s3c = boto3.client(
            's3',
            aws_access_key_id=app.config['S3_KEY'],
            aws_secret_access_key=app.config['S3_SECRET']
        )

    def __getattr__(self, name):
        return getattr(self.s3, name)
