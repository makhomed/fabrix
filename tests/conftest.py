import re
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
                    pytest.fail("Pattern '%s' not found in '%s'" % (self.regexp, value.message))
        return suppress_exception


def abort(regexp):
    return AbortContext(regexp)


class _AttributeString(str):
    pass


def mock_os_path_exists_factory(os_path_exists_state):  # os_path_exists_state == { pattern: True, pattern: False, ... }

    def mock_os_path_exists(command):
        for pattern, exists in os_path_exists_state.items():
            if re.match(pattern, command):
                return exists
        assert 0, 'command \'%s\' does not match any pattern' % command
    return mock_os_path_exists


def mock_run_factory(run_state):  # run_state == { pattern: { stdout: text, failed: boolean }, pattern: ... }

    def mock_run(command):
        for pattern, config in run_state.items():
            if re.match(pattern, command):
                out = _AttributeString(config['stdout'])
                out.failed = config['failed']
                return out
        assert 0, 'command \'%s\' does not match any pattern' % command
    return mock_run


def mock_local_factory(local_state):  # local_state == { pattern: { stdout: text, failed: boolean }, pattern: ... }

    def mock_local(command, **kwargs):
        assert kwargs is not None
        for pattern, config in local_state.items():
            if re.match(pattern, command):
                out = _AttributeString(config['stdout'])
                out.failed = config['failed']
                return out
        assert 0, 'command \'%s\' does not match any pattern' % command
    return mock_local


def mock_put_factory(put_state):  # put_state == { pattern : boolean, pattern: ... }

    def mock_put(**kwargs):
        remote_path = kwargs['remote_path']
        for pattern, failed in put_state.items():
            if re.match(pattern, remote_path):
                out = _AttributeString(list(('a', 'b', 'c')))
                out.failed = failed
                return out
        assert 0, 'remote_path does not match any pattern'
    return mock_put


def mock_get_factory(get_state):  # get_state == { pattern : { content: text, failed: boolean}, pattern: ... }

    def mock_get(**kwargs):
        file_like_object = kwargs['local_path']
        remote_path = kwargs['remote_path']
        for pattern, config in get_state.items():
            if re.match(pattern, remote_path):
                file_like_object.seek(0)
                file_like_object.write(config['content'])
                out = _AttributeString(list(('a', 'b', 'c')))
                out.failed = config['failed']
                return out
        assert 0, 'remote_path does not match any pattern'
    return mock_get
