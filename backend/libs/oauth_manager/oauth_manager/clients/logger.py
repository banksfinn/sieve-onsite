from logging_manager.logger import get_logger as _get_logger


def get_logger():
    """Get a logger bound to the oauth_manager context."""
    return _get_logger().bind(module="oauth_manager")
