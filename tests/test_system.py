import time
import fabrix.system
from conftest import mock_run_factory
from fabric.api import env
from fabrix.system import is_reboot_required, reboot_and_wait, disable_selinux


def test_is_reboot_required(monkeypatch):
    run_state = {
        r'if \[ ! -e /usr/bin/needs-restarting \] ; then echo notexists ; fi': {'stdout': 'notexists', 'failed': False},
        r'yum -y install yum-utils': {'stdout': '', 'failed': False},
        r'/usr/bin/needs-restarting -r': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert is_reboot_required() is False
    run_state = {
        r'if \[ ! -e /usr/bin/needs-restarting \] ; then echo notexists ; fi': {'stdout': '', 'failed': False},
        r'/usr/bin/needs-restarting -r': {'stdout': 'Reboot is required to ensure that your system benefits from these updates.', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert is_reboot_required() is True


def test_reboot_and_wait(monkeypatch):
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    run_state = {
        r'reboot': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    monkeypatch.setattr(fabrix.system.connections, 'connect', lambda x: None)
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    assert reboot_and_wait() is None


def test_disable_selinux(monkeypatch):
    run_state = {
        r'if \[ -e /etc/selinux/config \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
        r'if \[ -e /usr/sbin/setenforce \] && \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
        r'STATUS=\$\(getenforce\) ; if \[ "\$STATUS" == "Enforcing" \] ; then setenforce 0 ; echo perm ; fi': {'stdout': 'perm', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    monkeypatch.setattr(fabrix.system, 'edit_file', lambda x, y: True)
    assert disable_selinux() is True
    run_state = {
        r'if \[ -e /etc/selinux/config \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
        r'if \[ -e /usr/sbin/setenforce \] && \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert disable_selinux() is False
