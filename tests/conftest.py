import pytest
from fabric.api import env


@pytest.fixture(autouse=True)
def clear_fabric_config():
    env.hosts = list()
    env.roledefs = dict()
    env.host_string = None
    env.real_fabfile = None
    yield
    env.hosts = list()
    env.roledefs = dict()
    env.host_string = None
    env.real_fabfile = None


class AbortContext(object):
    def __init__(self, regexp):
        self.regexp = regexp

    def __enter__(self):
        pass

    def __exit__(self, extype, value, traceback):
        if extype is None:
            pytest.fail("DID NOT RAISE {0}".format(SystemExit))
        suppress_exception = issubclass(extype, SystemExit)
        if suppress_exception:
            import sys
            if sys.version_info.major == 2:
                sys.exc_clear()
            if self.regexp:
                import re
                if not re.match(self.regexp, str(value.message), re.DOTALL):
                    pytest.fail("Pattern '{0!s}' not found in '{1!s}'".format(self.regexp, value.message))
        return suppress_exception


def abort(regexp):
    return AbortContext(regexp)
