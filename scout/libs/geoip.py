import pygeoip

class Geoip(object):
    app = None
    pygeoip = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('GEOCITY_DAT_LOCATION', 'GeoLiteCity.dat')
        self.pygeoip = pygeoip.GeoIP(app.config['GEOCITY_DAT_LOCATION'])
        self.app = app

    def ipquery(self, ip):
        if not self.pygeoip:
            raise ValueError('A valid app instance has not been provided')
        return self.pygeoip.record_by_name(str(ip))
