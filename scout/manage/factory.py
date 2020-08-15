from flask_script import Manager

from scout import factory
from scout import manage
from scout.helpers import register_commands


def create_manager(package_name=None, package_path=None):
    if package_name is None:
        package_name = manage.__name__

    if package_path is None:
        package_path = manage.__path__

    """Returns the Bitbace command line manager application instance"""
    app = factory.create_app(package_name, package_path)
    manager = Manager(app)
    register_commands(manager, package_name, package_path)
    return manager
