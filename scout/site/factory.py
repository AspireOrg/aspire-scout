from scout.libs.aspire import Aspire
from datetime import datetime
from flask_assets import Bundle
from flask import request

from scout import factory
from scout import site
from scout.core import aspire
from scout.core import assets
from scout.site.forms import SearchForm


def create_app(package_name=None, package_path=None):
    if package_name is None:
        package_name = __name__

    if package_path is None:
        package_path = site.__path__

    app = factory.create_app(package_name, package_path, template_folder='site/templates', static_folder='site/static')

    assets.init_app(app)

    scss = Bundle('styles/base.scss', filters='scss', output='gen/packed.css')
    assets.register('scss_all', scss)

    js = Bundle('js/base.js', filters='jsmin', output='gen/packed.js')
    assets.register('js_all', js)

    from scout.site.views import bp
    app.register_blueprint(bp)

    from scout.site.api import bp
    app.register_blueprint(bp)

    def humanize_ts(timestamp=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.now()
        diff = now - datetime.fromtimestamp(timestamp)
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(int(second_diff)) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                v = int(second_diff / 60)
                if v == 1:
                    return "a minute ago"
                return str(int(second_diff / 60)) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                v = int(second_diff / 3600)
                if v == 1:
                    return "an hour ago"
                return str(int(second_diff / 3600)) + " hours ago"
        if day_diff == 1:
            return "yesterday"
        if day_diff < 7:
            if day_diff == 1:
                return str(day_diff) + " day ago"
            return str(day_diff) + " days ago"
        if day_diff < 31:
            v = int(day_diff / 7)
            if v == 1:
                return "a week ago"
            return str(v) + " weeks ago"
        if day_diff < 365:
            v = int(day_diff / 30)
            if v == 1:
                return "a month ago"
            return str(v) + " months ago"
        v = int(day_diff / 365)
        if v == 1:
            return "a year ago"
        return str(v) + " years ago"

    app.jinja_env.filters['humanize'] = humanize_ts

    @app.context_processor
    def inject_running_info():

        search_form = SearchForm()
        if request.method == 'POST' and request.form.get('is_search', False):
            if search_form.validate():
                flash('Searched', 'danger')
                return redirect('index')

        return {'running_info': aspire.aspired('get_running_info'), 'search_form': search_form}

    return app
